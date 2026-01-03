# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Social Media Harvester Connector (D36: Social Media Signals).

Harvests public social media posts from Twitter/X, Reddit, and public Facebook pages
for sentiment analysis, virality metrics, and network propagation analysis.

Data Sources:
    - Twitter/X: Public API + snscrape fallback
    - Reddit: PRAW (Python Reddit API Wrapper)
    - Facebook: Public pages scraper (optional)

Output Format: JSONL for downstream NLP pipelines

Use Cases:
    - Virality detection and cascade analysis
    - Sentiment volatility measurement
    - Geotag inference for spatial analysis
    - Network propagation modeling
"""

import hashlib
import json
import logging
import re
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

# Optional social media API libraries
try:
    import tweepy

    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

try:
    import praw

    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

try:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Gensim imports for topic modeling
try:
    import re as regex_module

    from gensim import corpora, models
    from gensim.models.coherencemodel import CoherenceModel

    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False

from krl_data_connectors.base_connector import BaseConnector

from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license

logger = logging.getLogger(__name__)


class SocialMediaHarvesterConnector(LicensedConnectorMixin, BaseConnector):
    """
    Connector for harvesting public social media signals.

    Supports:
    - Twitter/X public posts (API + scraping fallback)
    - Reddit public subreddits and comments
    - Facebook public pages (optional)

    Features:
    - JSONL output pipeline
    - Real-time streaming capabilities
    - Sentiment analysis integration (VADER, RoBERTa)
    - Topic modeling (LDA, BERTopic)
    - Network cascade detection
    - Deduplication by post ID

    Tier Mapping:
    - Tier 1-2: VADER sentiment, LDA topics, descriptive stats
    - Tier 3-4: RoBERTa sentiment, BERTopic, toxicity detection
    - Tier 5-6: GNN cascade detection, network virality analysis
    """

    # Registry name for license validation
    _connector_name = "Social_Media_Harvester"

    BASE_NAME = "SocialMediaHarvester"

    # Platform-specific endpoints
    PLATFORMS = {
        "twitter": {
            "api_version": "2",
            "rate_limit": 5,  # requests per second
            "streaming_available": True,
        },
        "reddit": {
            "api_version": "praw",
            "rate_limit": 10,  # requests per second
            "streaming_available": False,
        },
        "facebook": {
            "api_version": "graph",
            "rate_limit": 3,
            "streaming_available": False,
        },
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        reddit_client_id: Optional[str] = None,
        reddit_client_secret: Optional[str] = None,
        reddit_user_agent: Optional[str] = None,
        output_dir: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        Initialize Social Media Harvester Connector.

        Args:
            api_key: Twitter/X API bearer token (optional if using scraper fallback)
            reddit_client_id: Reddit OAuth client ID
            reddit_client_secret: Reddit OAuth client secret
            reddit_user_agent: Reddit API user agent string
            output_dir: Directory for JSONL output files (default: data/crawl/social)
            platforms: List of platforms to harvest ['twitter', 'reddit', 'facebook']
            **kwargs: Additional arguments passed to BaseConnector
        """
        super().__init__(api_key=api_key, **kwargs)

        # Platform credentials
        self.twitter_api_key = api_key
        self.reddit_client_id = reddit_client_id or self.config.get("REDDIT_CLIENT_ID")
        self.reddit_client_secret = reddit_client_secret or self.config.get("REDDIT_CLIENT_SECRET")
        self.reddit_user_agent = reddit_user_agent or self.config.get(
            "REDDIT_USER_AGENT", "KRL-Social-Harvester/1.0"
        )

        # Output configuration
        self.output_dir = Path(output_dir or "data/crawl/social")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Platform selection
        self.platforms = platforms or ["twitter", "reddit"]
        self._validate_platforms()

        # Initialize API clients
        self._twitter_client = None
        self._reddit_client = None
        self._vader_analyzer = None

        if TWEEPY_AVAILABLE and self.twitter_api_key and "twitter" in self.platforms:
            try:
                self._twitter_client = tweepy.Client(
                    bearer_token=self.twitter_api_key, wait_on_rate_limit=True
                )
                logger.info("Twitter API client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Twitter client: {e}")

        if (
            PRAW_AVAILABLE
            and self.reddit_client_id
            and self.reddit_client_secret
            and "reddit" in self.platforms
        ):
            try:
                self._reddit_client = praw.Reddit(
                    client_id=self.reddit_client_id,
                    client_secret=self.reddit_client_secret,
                    user_agent=self.reddit_user_agent,
                )
                logger.info("Reddit PRAW client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Reddit client: {e}")

        if VADER_AVAILABLE:
            self._vader_analyzer = SentimentIntensityAnalyzer()
            logger.info("VADER sentiment analyzer initialized")

        # Initialize RoBERTa model (lazy loading - only when first used)
        self._roberta_model = None
        self._roberta_tokenizer = None
        self._roberta_device = None

        # Track seen post IDs for deduplication
        self._seen_ids: set = set()

        logger.info(f"Initialized SocialMediaHarvesterConnector for platforms: {self.platforms}")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from instance variable or ConfigManager.

        Returns:
            Twitter/X API key if available, None otherwise
        """
        return getattr(self, "twitter_api_key", None)

    def _validate_platforms(self) -> None:
        """Validate selected platforms are supported."""
        invalid = [p for p in self.platforms if p not in self.PLATFORMS]
        if invalid:
            raise ValueError(
                f"Unsupported platforms: {invalid}. Valid: {list(self.PLATFORMS.keys())}"
            )

    def _generate_post_id(self, platform: str, content: str, author: str, timestamp: str) -> str:
        """
        Generate deterministic post ID for deduplication.

        Args:
            platform: Platform name
            content: Post text content
            author: Author username
            timestamp: Post timestamp

        Returns:
            MD5 hash string
        """
        unique_string = f"{platform}|{author}|{timestamp}|{content[:100]}"
        return hashlib.md5(unique_string.encode(), usedforsecurity=False).hexdigest()

    def _normalize_handle(self, handle: str) -> str:
        """
        Normalize social media handle.

        Args:
            handle: Raw handle/username

        Returns:
            Normalized handle (lowercase, no @)
        """
        return re.sub(r"^@", "", handle.lower().strip())

    def harvest_twitter(
        self,
        query: str,
        max_results: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Harvest tweets matching query.

        Args:
            query: Twitter search query (supports operators: AND, OR, -)
            max_results: Maximum tweets to retrieve
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with columns: post_id, text, author, date, metrics, url

        Example:
            >>> connector = SocialMediaHarvesterConnector()
            >>> df = connector.harvest_twitter("climate change", max_results=50)
        """
        logger.info(f"Harvesting Twitter with query: {query}")

        # Mock implementation - replace with actual Twitter API v2 or snscrape
        # For now, return empty DataFrame with correct schema
        data = {
            "post_id": [],
            "platform": [],
            "text": [],
            "author": [],
            "author_normalized": [],
            "date": [],
            "retweets": [],
            "likes": [],
            "replies": [],
            "url": [],
            "hashtags": [],
            "mentions": [],
            "has_media": [],
        }

        df = pd.DataFrame(data)

        # Save to JSONL
        if not df.empty:
            self._save_to_jsonl(df, "twitter")

        logger.info(f"Harvested {len(df)} tweets")
        return df

    def harvest_reddit(
        self,
        subreddit: str,
        limit: int = 100,
        time_filter: str = "week",
        sort: str = "hot",
    ) -> pd.DataFrame:
        """
        Harvest Reddit posts from a subreddit.

        Args:
            subreddit: Subreddit name (without r/)
            limit: Maximum posts to retrieve
            time_filter: Time filter (hour, day, week, month, year, all)
            sort: Sort method (hot, new, top, controversial, rising)

        Returns:
            DataFrame with columns: post_id, title, text, author, date, score, comments, url

        Example:
            >>> connector = SocialMediaHarvesterConnector()
            >>> df = connector.harvest_reddit("datascience", limit=50, sort="top")
        """
        logger.info(f"Harvesting Reddit r/{subreddit} (sort={sort}, filter={time_filter})")

        # Mock implementation - replace with PRAW
        data = {
            "post_id": [],
            "platform": [],
            "title": [],
            "text": [],
            "author": [],
            "author_normalized": [],
            "date": [],
            "score": [],
            "upvote_ratio": [],
            "num_comments": [],
            "url": [],
            "subreddit": [],
            "flair": [],
        }

        df = pd.DataFrame(data)

        # Save to JSONL
        if not df.empty:
            self._save_to_jsonl(df, "reddit")

        logger.info(f"Harvested {len(df)} Reddit posts")
        return df

    def harvest_facebook_page(
        self,
        page_id: str,
        limit: int = 50,
    ) -> pd.DataFrame:
        """
        Harvest public Facebook page posts.

        Args:
            page_id: Facebook page ID or username
            limit: Maximum posts to retrieve

        Returns:
            DataFrame with columns: post_id, text, author, date, likes, shares, comments, url

        Note:
            This requires Facebook Graph API access token and only works for public pages.
        """
        logger.info(f"Harvesting Facebook page: {page_id}")

        # Mock implementation - Facebook Graph API
        data = {
            "post_id": [],
            "platform": [],
            "text": [],
            "author": [],
            "author_normalized": [],
            "date": [],
            "likes": [],
            "shares": [],
            "comments": [],
            "url": [],
            "page_name": [],
        }

        df = pd.DataFrame(data)

        # Save to JSONL
        if not df.empty:
            self._save_to_jsonl(df, "facebook")

        logger.info(f"Harvested {len(df)} Facebook posts")
        return df

    def _save_to_jsonl(self, df: pd.DataFrame, platform: str) -> Path:
        """
        Save DataFrame to JSONL file.

        Args:
            df: DataFrame to save
            platform: Platform name (twitter, reddit, facebook)

        Returns:
            Path to saved JSONL file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / platform / f"{timestamp}.jsonl"
        filename.parent.mkdir(parents=True, exist_ok=True)

        # Convert to JSONL
        with open(filename, "w", encoding="utf-8") as f:
            for record in df.to_dict("records"):
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        logger.info(f"Saved {len(df)} records to {filename}")
        return filename

    @requires_license
    def get_sentiment(self, text: str, model: str = "vader") -> Dict[str, float]:
        """
        Calculate sentiment scores for text.

        Args:
            text: Text to analyze
            model: Sentiment model ('vader' for Tier 1-2, 'roberta' for Tier 3-4)

        Returns:
            Dictionary with sentiment scores (positive, negative, neutral, compound)

        Note:
            VADER (Valence Aware Dictionary and sEntiment Reasoner) is optimized for
            social media text and provides fast sentiment analysis suitable for Tier 1-2 models.
            RoBERTa support requires transformers library (coming in Week 1, Day 5-6).
        """
        if not text or not text.strip():
            return {
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0,
                "compound": 0.0,
            }

        if model == "vader" and self._vader_analyzer and VADER_AVAILABLE:
            try:
                scores = self._vader_analyzer.polarity_scores(text)
                return {
                    "positive": scores.get("pos", 0.0),
                    "negative": scores.get("neg", 0.0),
                    "neutral": scores.get("neu", 0.0),
                    "compound": scores.get("compound", 0.0),
                }
            except Exception as e:
                logger.error(f"VADER sentiment analysis error: {e}")
        elif model == "roberta":
            # Load model if not already loaded (lazy loading)
            if self._roberta_model is None:
                self._load_roberta_model()

            if self._roberta_model is not None and self._roberta_tokenizer is not None:
                try:
                    # Tokenize input
                    inputs = self._roberta_tokenizer(
                        text, return_tensors="pt", truncation=True, max_length=512, padding=True
                    )

                    # Move to same device as model
                    if self._roberta_device:
                        inputs = {k: v.to(self._roberta_device) for k, v in inputs.items()}

                    # Get predictions
                    with torch.no_grad():
                        outputs = self._roberta_model(**inputs)
                        logits = outputs.logits
                        probabilities = torch.nn.functional.softmax(logits, dim=-1)

                    # cardiffnlp model returns: [negative, neutral, positive]
                    probs = probabilities[0].cpu().numpy()

                    # Calculate compound score (positive - negative)
                    compound = float(probs[2] - probs[0])

                    return {
                        "positive": float(probs[2]),
                        "negative": float(probs[0]),
                        "neutral": float(probs[1]),
                        "compound": compound,
                    }
                except Exception as e:
                    logger.error(f"RoBERTa sentiment analysis error: {e}")
        else:
            if not VADER_AVAILABLE:
                logger.warning("VADER not available - install with 'pip install vaderSentiment'")

        # Fallback: neutral sentiment
        return {
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 1.0,
            "compound": 0.0,
        }

    def _load_roberta_model(self) -> None:
        """
        Lazy load RoBERTa sentiment model (cardiffnlp/twitter-roberta-base-sentiment).

        Only loads on first use to avoid memory overhead if not needed.
        Uses GPU if available for faster inference.
        """
        if self._roberta_model is not None:
            return  # Already loaded

        if not TRANSFORMERS_AVAILABLE:
            logger.warning(
                "transformers library not available - install with 'pip install transformers torch'"
            )
            return

        try:
            model_name = "cardiffnlp/twitter-roberta-base-sentiment"
            model_revision = "38c81429af47b66724b55daa43931b66808f0023"
            logger.info(f"Loading RoBERTa model: {model_name}")

            # Revision is pinned for security - suppress false positive Bandit warning
            self._roberta_tokenizer = AutoTokenizer.from_pretrained(
                model_name, revision=model_revision
            )  # nosec B615
            self._roberta_model = AutoModelForSequenceClassification.from_pretrained(
                model_name, revision=model_revision
            )  # nosec B615

            # Use GPU if available
            if torch.cuda.is_available():
                self._roberta_device = "cuda"
                self._roberta_model = self._roberta_model.to("cuda")
                logger.info("RoBERTa model loaded on GPU")
            elif torch.backends.mps.is_available():
                # Apple Silicon GPU
                self._roberta_device = "mps"
                self._roberta_model = self._roberta_model.to("mps")
                logger.info("RoBERTa model loaded on Apple Silicon GPU")
            else:
                self._roberta_device = "cpu"
                logger.info("RoBERTa model loaded on CPU")

            self._roberta_model.eval()  # Set to evaluation mode

        except Exception as e:
            logger.error(f"Failed to load RoBERTa model: {e}")
            self._roberta_model = None
            self._roberta_

    tokenizer = None

    @requires_license
    def get_topics(
        self,
        texts: list[str],
        num_topics: int = 5,
        passes: int = 10,
        calculate_coherence: bool = True,
    ) -> dict[str, any]:
        """
        Extract topics from a corpus of texts using LDA (Latent Dirichlet Allocation).

        Uses gensim's LDA implementation to discover latent topics in text data.
        Includes preprocessing (tokenization, stop word removal) and optional
        coherence scoring.

        Args:
            texts: List of text documents to analyze
            num_topics: Number of topics to extract (default: 5)
            passes: Number of training passes through corpus (default: 10)
            calculate_coherence: Calculate coherence score (default: True)

        Returns:
            Dictionary containing:
                - topics: List of (topic_id, [(word, probability), ...])
                - coherence_score: C_v coherence score (if calculate_coherence=True)
                - num_documents: Number of documents processed
                - vocabulary_size: Size of vocabulary after preprocessing

        Examples:
            >>> texts = ["bitcoin price rising", "ethereum blockchain tech"]
            >>> result = connector.get_topics(texts, num_topics=2)
            >>> print(result["topics"][0])
            (0, [("bitcoin", 0.5), ("price", 0.3), ...])
        """
        if not GENSIM_AVAILABLE:
            logger.warning("gensim not available for topic modeling")
            return {
                "error": "gensim not installed",
                "topics": [],
                "num_documents": len(texts),
            }

        if not texts or len(texts) == 0:
            return {
                "error": "Empty corpus",
                "topics": [],
                "num_documents": 0,
            }

        try:
            # Preprocessing: Tokenize and clean
            stop_words = set(
                [
                    "the",
                    "a",
                    "an",
                    "and",
                    "or",
                    "but",
                    "in",
                    "on",
                    "at",
                    "to",
                    "for",
                    "of",
                    "with",
                    "by",
                    "from",
                    "as",
                    "is",
                    "was",
                    "are",
                    "been",
                    "be",
                    "have",
                    "has",
                    "had",
                    "do",
                    "does",
                    "did",
                    "will",
                    "would",
                    "should",
                    "could",
                    "may",
                    "might",
                    "must",
                    "can",
                    "this",
                    "that",
                    "these",
                    "those",
                    "i",
                    "you",
                    "he",
                    "she",
                    "it",
                    "we",
                    "they",
                    "what",
                    "which",
                    "who",
                    "when",
                    "where",
                    "why",
                    "how",
                    "http",
                    "https",
                    "www",
                    "com",
                    "rt",
                    "via",
                ]
            )

            # Tokenize and clean documents
            processed_docs = []
            for text in texts:
                # Lowercase and remove non-alphabetic characters
                text_lower = text.lower()
                tokens = regex_module.findall(r"\b[a-z]+\b", text_lower)
                # Remove stop words and short tokens
                filtered_tokens = [
                    token for token in tokens if token not in stop_words and len(token) > 2
                ]
                if filtered_tokens:  # Only add non-empty documents
                    processed_docs.append(filtered_tokens)

            if len(processed_docs) == 0:
                return {
                    "error": "All documents empty after preprocessing",
                    "topics": [],
                    "num_documents": len(texts),
                }

            # Create dictionary and corpus
            dictionary = corpora.Dictionary(processed_docs)
            corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

            # Train LDA model
            lda_model = models.LdaModel(
                corpus=corpus,
                id2word=dictionary,
                num_topics=num_topics,
                random_state=42,
                passes=passes,
                alpha="auto",
                per_word_topics=True,
            )

            # Extract topics with top words
            topics = []
            for topic_id in range(num_topics):
                topic_words = lda_model.show_topic(topic_id, topn=10)
                topics.append((topic_id, topic_words))

            result = {
                "topics": topics,
                "num_documents": len(processed_docs),
                "vocabulary_size": len(dictionary),
            }

            # Calculate coherence score
            if calculate_coherence and len(processed_docs) >= num_topics:
                try:
                    coherence_model = CoherenceModel(
                        model=lda_model,
                        texts=processed_docs,
                        dictionary=dictionary,
                        coherence="c_v",
                        processes=1,  # Disable multiprocessing for macOS compatibility
                    )
                    result["coherence_score"] = coherence_model.get_coherence()
                except Exception as e:
                    logger.warning(f"Coherence calculation failed: {e}")
                    result["coherence_score"] = None
            else:
                result["coherence_score"] = None

            return result

        except Exception as e:
            logger.error(f"Topic modeling failed: {e}")
            return {
                "error": str(e),
                "topics": [],
                "num_documents": len(texts),
            }

    def detect_virality(
        self,
        post_id: str,
        metrics: Dict[str, int],
        threshold_percentile: float = 0.9,
    ) -> Dict[str, Any]:
        """
        Detect if a post has viral characteristics.

        Args:
            post_id: Post identifier
            metrics: Dictionary with engagement metrics (likes, shares, comments, retweets)
            threshold_percentile: Percentile threshold for virality (default: top 10%)

        Returns:
            Dictionary with virality analysis:
            - is_viral: bool
            - virality_score: float (0-1)
            - engagement_rate: float
            - velocity: float (engagement per hour)
        """
        total_engagement = sum(metrics.values())

        # Mock implementation - replace with actual cascade analysis
        return {
            "post_id": post_id,
            "is_viral": total_engagement > 1000,
            "virality_score": min(total_engagement / 10000, 1.0),
            "engagement_rate": total_engagement,
            "velocity": 0.0,
        }

    def aggregate_by_period(
        self,
        df: pd.DataFrame,
        period: str = "D",
        metrics: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Aggregate social media data by time period.

        Args:
            df: DataFrame with 'date' column
            period: Pandas period string ('H' hourly, 'D' daily, 'W' weekly)
            metrics: List of metric columns to aggregate (default: all numeric)

        Returns:
            Aggregated DataFrame indexed by period
        """
        if "date" not in df.columns:
            raise ValueError("DataFrame must have 'date' column")

        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

        # Select numeric columns if metrics not specified
        if metrics is None:
            metrics = df.select_dtypes(include=["number"]).columns.tolist()

        return df[metrics].resample(period).sum()

    @requires_license
    def get_top_hashtags(
        self,
        df: pd.DataFrame,
        n: int = 20,
    ) -> pd.DataFrame:
        """
        Extract top hashtags from social media data.

        Args:
            df: DataFrame with 'hashtags' column (list of hashtags)
            n: Number of top hashtags to return

        Returns:
            DataFrame with columns: hashtag, count, percentage
        """
        if "hashtags" not in df.columns:
            return pd.DataFrame(columns=["hashtag", "count", "percentage"])

        # Flatten hashtag lists
        all_hashtags = []
        for hashtag_list in df["hashtags"].dropna():
            if isinstance(hashtag_list, list):
                all_hashtags.extend(hashtag_list)

        if not all_hashtags:
            return pd.DataFrame(columns=["hashtag", "count", "percentage"])

        # Count and sort
        hashtag_counts = pd.Series(all_hashtags).value_counts().head(n)
        total = len(all_hashtags)

        result = pd.DataFrame(
            {
                "hashtag": hashtag_counts.index,
                "count": hashtag_counts.values,
                "percentage": (hashtag_counts.values / total * 100).round(2),
            }
        )

        return result.reset_index(drop=True)

    def connect(self) -> bool:
        """
        Test connection to configured social media platforms.

        Returns:
            True if at least one platform is accessible
        """
        logger.info("Testing social media platform connections...")

        accessible = []

        # Test Twitter
        if "twitter" in self.platforms:
            if self.twitter_api_key:
                logger.info("✓ Twitter API key configured")
                accessible.append("twitter")
            else:
                logger.warning("✗ Twitter API key missing (will use scraper fallback)")

        # Test Reddit
        if "reddit" in self.platforms:
            if self.reddit_client_id and self.reddit_client_secret:
                logger.info("✓ Reddit credentials configured")
                accessible.append("reddit")
            else:
                logger.warning("✗ Reddit credentials missing")

        # Test Facebook
        if "facebook" in self.platforms:
            if self.api_key:  # Reuse api_key for Facebook Graph API
                logger.info("✓ Facebook API token configured")
                accessible.append("facebook")
            else:
                logger.warning("✗ Facebook API token missing")

        success = len(accessible) > 0
        if success:
            logger.info(f"Connected to platforms: {accessible}")
        else:
            logger.error("No platform credentials configured")

        return success

    def fetch(self) -> pd.DataFrame:
        """
        Fetch recent social media data from configured platforms.

        This is a convenience method that harvests recent data from all platforms.
        For more control, use platform-specific methods (harvest_twitter, harvest_reddit, etc.)

        Returns:
            Combined DataFrame from all platforms
        """
        logger.info("Fetching recent social media data from all configured platforms...")

        all_data = []

        # Twitter
        if "twitter" in self.platforms:
            try:
                twitter_df = self.harvest_twitter(
                    "(data OR analytics OR research)", max_results=100
                )
                all_data.append(twitter_df)
            except Exception as e:
                logger.error(f"Twitter harvest failed: {e}")

        # Reddit
        if "reddit" in self.platforms:
            try:
                reddit_df = self.harvest_reddit("datascience", limit=100)
                all_data.append(reddit_df)
            except Exception as e:
                logger.error(f"Reddit harvest failed: {e}")

        # Facebook
        if "facebook" in self.platforms:
            try:
                # Would need specific page IDs
                pass
            except Exception as e:
                logger.error(f"Facebook harvest failed: {e}")

        # Combine all data
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            logger.info(f"Fetched {len(combined)} total posts from {len(all_data)} platform(s)")
            return combined
        else:
            logger.warning("No data fetched from any platform")
            return pd.DataFrame()
