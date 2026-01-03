# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: LicenseRef-KRL-Professional
# License Tier: Professional ($49/month) or Enterprise ($299/month)
# ----------------------------------------------------------------------

"""
Advanced Sentiment Analysis

Part of KRL Media Intelligence Module (Professional Tier)

Multi-level sentiment extraction from full-text articles using
transformer models with aspect-based analysis capabilities.

Improvements over basic sentiment on titles:
- Context-aware sentiment (full article vs headline)
- Aspect-based sentiment (policy, workers, companies)
- Sentiment trajectory detection (how sentiment shifts within article)

Trade Secrets:
- Aspect keyword dictionaries
- Chunk aggregation algorithm
- Trajectory detection thresholds

This module is CONFIDENTIAL and proprietary to KR-Labs.
Unauthorized copying, distribution, or reverse engineering is prohibited.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


@dataclass
class SentimentResult:
    """Container for sentiment analysis results."""
    overall_sentiment: str
    overall_score: float
    confidence: float
    trajectory: str
    chunk_count: int = 1
    aspects: Optional[Dict[str, float]] = None


class AdvancedSentimentAnalyzer:
    """
    Deep sentiment analysis using transformer models.
    
    Capabilities:
    - Overall article sentiment
    - Aspect-based sentiment (policy, workers, management)
    - Sentiment trajectory (does article sentiment shift?)
    
    License: Professional Tier ($49/month) or Enterprise ($299/month)
    
    Example:
        >>> from krl_data_connectors.core.media_intelligence import AdvancedSentimentAnalyzer
        >>> analyzer = AdvancedSentimentAnalyzer()
        >>> df_with_sentiment = analyzer.analyze_dataframe(df, text_column='full_text')
    """

    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        """
        Initialize sentiment analysis pipeline.
        
        Args:
            model_name: Hugging Face model name for sentiment analysis
        """
        print("🎭 Initializing Advanced Sentiment Analyzer...")
        print(f"   Loading transformer model: {model_name}")

        try:
            from transformers import pipeline
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                max_length=512,
                truncation=True
            )
            self.enabled = True
        except Exception as e:
            print(f"⚠️  Failed to load sentiment model: {e}")
            print("   Sentiment analysis will be skipped")
            self.enabled = False
            return

        # Aspect keywords for aspect-based sentiment
        self.aspect_keywords = {
            'workers': ['worker', 'employee', 'union', 'labor', 'staff', 'workforce'],
            'management': ['management', 'company', 'employer', 'corporation', 'executive'],
            'policy': ['policy', 'regulation', 'law', 'legislation', 'government'],
            'economy': ['economy', 'economic', 'wage', 'salary', 'income', 'cost']
        }

        print("✓ Sentiment analyzer ready")

    def analyze_text(self, text: str, chunk_size: int = 500) -> SentimentResult:
        """
        Analyze sentiment of full text.
        
        For long articles, analyzes in chunks and aggregates.
        
        Args:
            text: Article full text
            chunk_size: Words per chunk (transformer has 512 token limit)
            
        Returns:
            SentimentResult with overall sentiment and trajectory
        """
        if not self.enabled or not text or len(str(text).strip()) < 10:
            return SentimentResult(
                overall_sentiment='neutral',
                overall_score=0.0,
                confidence=0.0,
                trajectory='stable',
                chunk_count=0
            )

        # Split into chunks
        words = str(text).split()
        chunks = [
            ' '.join(words[i:i+chunk_size])
            for i in range(0, len(words), chunk_size)
        ]

        # Analyze each chunk
        chunk_sentiments = []

        for chunk in chunks:
            try:
                result = self.sentiment_pipeline(chunk)[0]

                # Convert to numeric score (-1 to 1)
                label = result['label'].lower()
                score_map = {'negative': -1, 'neutral': 0, 'positive': 1}
                score = score_map.get(label, 0) * result['score']

                chunk_sentiments.append({
                    'label': label,
                    'score': score,
                    'confidence': result['score']
                })
            except Exception:
                continue

        if not chunk_sentiments:
            return SentimentResult(
                overall_sentiment='neutral',
                overall_score=0.0,
                confidence=0.0,
                trajectory='stable',
                chunk_count=0
            )

        # Aggregate sentiment
        avg_score = np.mean([s['score'] for s in chunk_sentiments])
        avg_confidence = np.mean([s['confidence'] for s in chunk_sentiments])

        # Determine overall label
        if avg_score > 0.1:
            overall_label = 'positive'
        elif avg_score < -0.1:
            overall_label = 'negative'
        else:
            overall_label = 'neutral'

        # Detect sentiment trajectory
        trajectory = self._detect_trajectory(chunk_sentiments)

        return SentimentResult(
            overall_sentiment=overall_label,
            overall_score=float(avg_score),
            confidence=float(avg_confidence),
            trajectory=trajectory,
            chunk_count=len(chunk_sentiments)
        )

    def _detect_trajectory(self, chunk_sentiments: List[Dict]) -> str:
        """Detect how sentiment changes through the article."""
        if len(chunk_sentiments) < 3:
            return 'stable'
            
        scores = [s['score'] for s in chunk_sentiments]
        first_third = np.mean(scores[:len(scores)//3])
        last_third = np.mean(scores[-len(scores)//3:])

        if last_third - first_third > 0.2:
            return 'improving'
        elif first_third - last_third > 0.2:
            return 'declining'
        else:
            return 'stable'

    def analyze_aspects(self, text: str) -> Dict[str, float]:
        """
        Aspect-based sentiment analysis.
        
        Extracts sentiment for specific aspects:
        - Workers/unions
        - Management/companies
        - Policy/regulation
        - Economy/wages
        
        Args:
            text: Article full text
            
        Returns:
            Dict of {aspect: sentiment_score}
        """
        if not self.enabled or not text:
            return {aspect: 0.0 for aspect in self.aspect_keywords.keys()}

        aspect_sentiments = {}
        text_str = str(text)

        for aspect, keywords in self.aspect_keywords.items():
            # Find sentences mentioning this aspect
            sentences = text_str.split('.')
            relevant_sentences = [
                sent for sent in sentences
                if any(kw in sent.lower() for kw in keywords)
            ]

            if not relevant_sentences:
                aspect_sentiments[aspect] = 0.0
                continue

            # Analyze sentiment of relevant sentences
            aspect_text = '. '.join(relevant_sentences[:5])  # Max 5 sentences

            try:
                result = self.sentiment_pipeline(aspect_text[:512])[0]
                label = result['label'].lower()
                score_map = {'negative': -1, 'neutral': 0, 'positive': 1}
                score = score_map.get(label, 0) * result['score']
                aspect_sentiments[aspect] = float(score)
            except Exception:
                aspect_sentiments[aspect] = 0.0

        return aspect_sentiments

    def analyze_dataframe(
        self,
        df: pd.DataFrame,
        text_column: str = 'full_text',
        analyze_aspects: bool = True
    ) -> pd.DataFrame:
        """
        Analyze sentiment for entire DataFrame.
        
        Args:
            df: DataFrame with full text
            text_column: Column containing article text
            analyze_aspects: Whether to perform aspect-based analysis
            
        Returns:
            DataFrame with sentiment columns added
        """
        if not self.enabled:
            print("⚠️  Sentiment analyzer not enabled - skipping")
            return df

        print(f"\n🎭 Analyzing sentiment for {len(df):,} articles...")

        # Overall sentiment
        df_result = df.copy()
        sentiments = df_result[text_column].apply(self.analyze_text)

        df_result['sentiment_deep'] = sentiments.apply(lambda x: x.overall_sentiment)
        df_result['sentiment_deep_score'] = sentiments.apply(lambda x: x.overall_score)
        df_result['sentiment_confidence'] = sentiments.apply(lambda x: x.confidence)
        df_result['sentiment_trajectory'] = sentiments.apply(lambda x: x.trajectory)

        # Aspect-based sentiment
        if analyze_aspects:
            print("   Extracting aspect-based sentiment...")
            aspects = df_result[text_column].apply(self.analyze_aspects)

            for aspect in self.aspect_keywords.keys():
                df_result[f'sentiment_{aspect}'] = aspects.apply(lambda x: x.get(aspect, 0.0))

        # Summary statistics
        print(f"\n✓ Sentiment analysis complete")
        print(f"   Distribution:")
        print(df_result['sentiment_deep'].value_counts().to_string())

        if analyze_aspects:
            print(f"\n   Average aspect sentiments:")
            for aspect in self.aspect_keywords.keys():
                avg = df_result[f'sentiment_{aspect}'].mean()
                print(f"      {aspect.capitalize()}: {avg:+.3f}")

        return df_result
