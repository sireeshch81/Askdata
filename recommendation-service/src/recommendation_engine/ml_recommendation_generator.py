import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

from .database_connector import DatabaseConnector
from .dw_feature_calculator import DWFeatureCalculator

logger = logging.getLogger(__name__)

class MLRecommendationGenerator:
    """ML-based recommendation system using similarity clustering with Scikit-learn"""
    
    def __init__(self, db_connector: DatabaseConnector):
        self.db = db_connector
        self.feature_calculator = DWFeatureCalculator(db_connector)
        
        # ML Models
        self.scaler = RobustScaler()  # More robust to outliers than StandardScaler
        self.knn_model = None
        self.cluster_model = None
        self.pca_model = None
        
        # Feature matrices
        self.feature_matrix = None
        self.scaled_features = None
        self.customer_ids = None
        
        # Products cache
        self.products_df = None
        
        # Model configuration
        self.n_neighbors = 50
        self.n_clusters = 10
        self.pca_components = 15
        
    def load_products(self):
        """Load and cache financial products from DW"""
        try:
            if self.db.current_source != 'dw':
                self.db.connect('dw')
            
            self.products_df = self.db.get_dw_all_products()
            logger.info(f"Loaded {len(self.products_df)} financial products")
            
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            self.products_df = pd.DataFrame()
    
    def build_similarity_model(self, sample_size: int = 5000):
        """Build similarity model using customer feature vectors"""
        try:
            logger.info("Building ML similarity model...")
            
            # Ensure DW connection
            if self.db.current_source != 'dw':
                self.db.connect('dw')
            
            # Get sample of customers for model building
            customers_df = self.db.get_dw_batch_customers(batch_size=sample_size, offset=0)
            
            if customers_df.empty:
                logger.error("No customers found for model building")
                return False
            
            logger.info(f"Building model with {len(customers_df)} customers")
            
            # Calculate features for all customers
            customer_ids = customers_df['customer_id'].tolist()
            features_df = self.feature_calculator.calculate_batch_features(customer_ids)
            
            if features_df.empty:
                logger.error("No features calculated")
                return False
            
            # Prepare feature matrix
            self._prepare_feature_matrix(features_df)
            
            # Build models
            self._train_similarity_models()
            
            logger.info("✅ ML similarity model built successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error building similarity model: {e}")
            return False
    
    def _prepare_feature_matrix(self, features_df: pd.DataFrame):
        """Prepare and scale feature matrix for ML models"""
        # Store customer IDs
        self.customer_ids = features_df['customer_id'].values
        
        # Select numerical features (exclude customer_id)
        feature_columns = [col for col in features_df.columns if col != 'customer_id']
        self.feature_matrix = features_df[feature_columns].fillna(0)
        
        # Handle infinite values
        self.feature_matrix = self.feature_matrix.replace([np.inf, -np.inf], 0)
        
        # Scale features
        self.scaled_features = self.scaler.fit_transform(self.feature_matrix)
        
        logger.info(f"Feature matrix prepared: {self.scaled_features.shape}")
    
    def _train_similarity_models(self):
        """Train KNN, clustering, and dimensionality reduction models"""
        
        # 1. K-Nearest Neighbors for similarity search
        self.knn_model = NearestNeighbors(
            n_neighbors=min(self.n_neighbors, len(self.scaled_features)),
            metric='cosine',
            algorithm='brute'  # More accurate for cosine distance
        )
        self.knn_model.fit(self.scaled_features)
        
        # 2. K-Means clustering for customer segmentation
        self.cluster_model = KMeans(
            n_clusters=min(self.n_clusters, len(self.scaled_features)),
            random_state=42,
            n_init=10
        )
        cluster_labels = self.cluster_model.fit_predict(self.scaled_features)
        
        # 3. PCA for dimensionality reduction and feature importance
        self.pca_model = PCA(
            n_components=min(self.pca_components, self.scaled_features.shape[1])
        )
        self.pca_features = self.pca_model.fit_transform(self.scaled_features)
        
        logger.info(f"Models trained - KNN: {self.knn_model.n_neighbors}, "
                   f"Clusters: {self.cluster_model.n_clusters}, "
                   f"PCA components: {self.pca_model.n_components_}")
    
    def generate_recommendations(self, customer_id: str, top_n: int = 5) -> Optional[Dict]:
        """Generate ML-based recommendations for a customer"""
        try:
            if not self._models_ready():
                logger.error("Models not trained. Call build_similarity_model() first.")
                return None
            
            # Load products if not cached
            if self.products_df is None or self.products_df.empty:
                self.load_products()
            
            # Calculate customer features
            customer_features = self.feature_calculator.calculate_customer_features(customer_id)
            if not customer_features:
                logger.warning(f"Could not calculate features for customer {customer_id}")
                return None
            
            # Get customer profile for output
            customer_profile = self._build_customer_profile(customer_features)
            
            # Find similar customers
            similar_customers = self._find_similar_customers(customer_features, top_n * 3)
            
            # Generate product recommendations
            recommendations = self._generate_product_recommendations(
                customer_features, similar_customers, top_n
            )
            
            # Build final recommendation structure
            result = {
                "customer_id": customer_id,
                "customer_profile": customer_profile,
                "recommendations": recommendations,
                "created_at": datetime.now().isoformat(),
                "algorithm_type": "ml_similarity",
                "data_source": "dw"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating recommendations for {customer_id}: {e}")
            return None
    
    def _models_ready(self) -> bool:
        """Check if all models are trained and ready"""
        return (self.knn_model is not None and 
                self.cluster_model is not None and 
                self.scaled_features is not None)
    
    def _build_customer_profile(self, customer_features: Dict) -> Dict:
        """Build customer profile for output"""
        # Get full customer profile from DW
        full_profile = self.db.get_dw_customer_profile(customer_features['customer_id'])
        
        profile = {
            "name": full_profile.get('name', 'Unknown') if full_profile else 'Unknown',
            "annual_income": customer_features.get('annual_income', 0),
            "credit_score": customer_features.get('credit_score', 0),
            "health_score": customer_features.get('health_score', 0),
            "risk_category": self._decode_risk_category(customer_features.get('risk_category_encoded', 0)),
            "utilization_ratio": customer_features.get('utilization_ratio', 0)
        }
        
        return profile
    
    def _find_similar_customers(self, customer_features: Dict, n_similar: int = 15) -> List[Dict]:
        """Find similar customers using KNN and clustering"""
        
        # Prepare customer feature vector
        feature_vector = self._prepare_customer_vector(customer_features)
        
        # Find nearest neighbors
        distances, indices = self.knn_model.kneighbors([feature_vector], n_neighbors=n_similar)
        
        similar_customers = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.customer_ids):  # Safety check
                similar_customer_id = self.customer_ids[idx]
                
                # Get similarity score (convert distance to similarity)
                similarity_score = max(0, 1 - distance)  # Cosine distance to similarity
                
                similar_customers.append({
                    'customer_id': similar_customer_id,
                    'similarity_score': round(float(similarity_score), 3),
                    'rank': i + 1
                })
        
        return similar_customers
    
    def _prepare_customer_vector(self, customer_features: Dict) -> np.ndarray:
        """Prepare customer feature vector for similarity calculation"""
        feature_names = self.feature_calculator.get_feature_names()
        
        # Create feature vector in same order as training data
        feature_vector = []
        for feature_name in feature_names:
            if feature_name != 'customer_id':
                value = customer_features.get(feature_name, 0)
                # Handle infinite/nan values
                if np.isnan(value) or np.isinf(value):
                    value = 0
                feature_vector.append(value)
        
        # Scale using fitted scaler
        feature_vector = np.array(feature_vector).reshape(1, -1)
        scaled_vector = self.scaler.transform(feature_vector)
        
        return scaled_vector[0]
    
    def _generate_product_recommendations(self, 
                                        customer_features: Dict, 
                                        similar_customers: List[Dict], 
                                        top_n: int) -> List[Dict]:
        """Generate product recommendations based on similar customers"""
        
        if self.products_df.empty:
            return []
        
        # Get customer's existing products
        existing_products = self.db.get_dw_customer_product_history(customer_features['customer_id'])
        existing_product_ids = set(existing_products['product_id'].tolist()) if not existing_products.empty else set()
        
        # Score all products
        product_scores = {}
        
        for _, product in self.products_df.iterrows():
            product_id = product['product_id']
            
            # Skip if customer already has this product
            if product_id in existing_product_ids:
                continue
            
            # Calculate eligibility score
            eligibility_score = self._calculate_eligibility_score(customer_features, product)
            
            # Calculate similarity-based score
            similarity_score = self._calculate_similarity_score(product_id, similar_customers)
            
            # Calculate confidence based on feature alignment
            confidence_score = self._calculate_confidence_score(customer_features, product)
            
            # Combined score
            combined_score = (eligibility_score * 0.4 + 
                            similarity_score * 0.4 + 
                            confidence_score * 0.2)
            
            product_scores[product_id] = {
                'product': product,
                'score': combined_score,
                'eligibility_score': eligibility_score,
                'similarity_score': similarity_score,
                'confidence': confidence_score
            }
        
        # Sort and get top recommendations
        sorted_products = sorted(product_scores.items(), 
                               key=lambda x: x[1]['score'], 
                               reverse=True)
        
        recommendations = []
        for i, (product_id, scores) in enumerate(sorted_products[:top_n]):
            product = scores['product']
            
            # Generate recommendation reason
            reason = self._generate_recommendation_reason(
                customer_features, product, scores
            )
            
            recommendation = {
                "rank": i + 1,
                "product_name": product['product_name'],
                "product_type": product['product_type'],
                "score": round(scores['score'], 1),
                "max_score": 100.0,
                "confidence": round(scores['confidence'], 1),
                "reason": reason
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_eligibility_score(self, customer_features: Dict, product: pd.Series) -> float:
        """Calculate eligibility score based on product criteria"""
        score = 100.0
        
        # Credit score requirement
        min_credit = product.get('min_credit_score', 0)
        if min_credit > 0:
            customer_credit = customer_features.get('credit_score', 0)
            if customer_credit < min_credit:
                score *= 0.3  # Heavy penalty for not meeting minimum
            elif customer_credit >= min_credit + 50:
                score *= 1.1  # Bonus for exceeding by significant margin
        
        # Income requirement
        min_income = product.get('min_income', 0)
        if min_income > 0:
            customer_income = customer_features.get('annual_income', 0)
            if customer_income < min_income:
                score *= 0.4
            elif customer_income >= min_income * 1.5:
                score *= 1.1
        
        # Debt-to-income ratio
        max_dti = product.get('max_debt_to_income', 1.0)
        if max_dti > 0:
            customer_dti = customer_features.get('debt_to_income_ratio', 0)
            if customer_dti > max_dti:
                score *= 0.5
        
        return min(score, 100.0)
    
    def _calculate_similarity_score(self, product_id: str, similar_customers: List[Dict]) -> float:
        """Calculate score based on similar customers' product usage"""
        if not similar_customers:
            return 50.0  # Neutral score if no similar customers
        
        # In a full implementation, you would check which similar customers
        # have this product and weight by their similarity scores
        # For now, using a simplified approach
        
        # Assume higher similarity customers contribute more to the score
        weighted_score = 0
        total_weight = 0
        
        for customer in similar_customers[:10]:  # Top 10 similar customers
            similarity = customer['similarity_score']
            
            # In practice, you'd query if this customer has the product
            # For demonstration, using a probabilistic approach
            has_product_probability = similarity * 0.8  # Simplified
            
            weighted_score += has_product_probability * similarity * 100
            total_weight += similarity
        
        return weighted_score / total_weight if total_weight > 0 else 50.0
    
    def _calculate_confidence_score(self, customer_features: Dict, product: pd.Series) -> float:
        """Calculate confidence score based on feature alignment"""
        
        # Health score alignment
        health_score = customer_features.get('health_score', 0)
        
        # Credit utilization alignment  
        utilization = customer_features.get('utilization_ratio', 0)
        
        # Risk category alignment
        risk_encoded = customer_features.get('risk_category_encoded', 0)
        
        # Simple confidence calculation
        confidence = 50.0  # Base confidence
        
        if health_score > 70:
            confidence += 20
        elif health_score > 50:
            confidence += 10
        
        if utilization < 0.3:
            confidence += 15
        elif utilization < 0.7:
            confidence += 5
        
        if risk_encoded == 1:  # Low risk
            confidence += 15
        elif risk_encoded == 2:  # Medium risk
            confidence += 5
        
        return min(confidence, 100.0)
    
    def _generate_recommendation_reason(self, 
                                      customer_features: Dict, 
                                      product: pd.Series, 
                                      scores: Dict) -> str:
        """Generate human-readable recommendation reason"""
        
        reasons = []
        
        # Credit score based reason
        credit_score = customer_features.get('credit_score', 0)
        if credit_score >= 750:
            reasons.append("Excellent credit score")
        elif credit_score >= 700:
            reasons.append("Good credit score")
        
        # Health score based reason
        health_score = customer_features.get('health_score', 0)
        if health_score > 75:
            reasons.append("Strong financial health")
        
        # Similar customers reason
        if scores['similarity_score'] > 70:
            reasons.append("Similar customers frequently choose this product")
        
        # Income alignment
        annual_income = customer_features.get('annual_income', 0)
        if annual_income > 75000:
            reasons.append("Income level aligns well")
        
        # Default reason if no specific reasons
        if not reasons:
            reasons.append("Profile matches product criteria")
        
        return "; ".join(reasons[:2])  # Limit to 2 main reasons
    
    def _decode_risk_category(self, risk_encoded: int) -> str:
        """Decode risk category from numeric to text"""
        risk_mapping = {1: 'low', 2: 'medium', 3: 'high', 0: 'unknown'}
        return risk_mapping.get(risk_encoded, 'unknown')
    
    def get_model_stats(self) -> Dict:
        """Get statistics about the trained models"""
        if not self._models_ready():
            return {"error": "Models not trained"}
        
        return {
            "total_customers": len(self.customer_ids),
            "feature_dimensions": self.scaled_features.shape[1],
            "n_neighbors": self.knn_model.n_neighbors,
            "n_clusters": self.cluster_model.n_clusters,
            "pca_explained_variance": float(self.pca_model.explained_variance_ratio_.sum()) if self.pca_model else 0,
            "available_products": len(self.products_df) if self.products_df is not None else 0
        }
