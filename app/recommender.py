# Job recommendation engine
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK resources if not already available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class JobRecommender:
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.job_dataframe = None
    
    def preprocess_text(self, text):
        """Preprocess text by cleaning, tokenizing, removing stopwords, and lemmatizing"""
        if not isinstance(text, str) or pd.isna(text):
            return ''
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs, email addresses, special characters, and numbers
        text = re.sub(r'http\S+|www\S+|https\S+', ' ', text)
        text = re.sub(r'\S+@\S+', ' ', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        # Add custom domain-specific stopwords
        custom_stopwords = {'job', 'work', 'company', 'position', 'required', 'requirements',
                           'experience', 'skill', 'skills', 'candidate', 'opportunity', 'role'}
        stop_words.update(custom_stopwords)
        tokens = [word for word in tokens if word not in stop_words]
        
        # Lemmatize
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        
        # Remove short words (length < 3)
        tokens = [word for word in tokens if len(word) >= 3]
        
        # Join tokens back into text
        return ' '.join(tokens)
    
    def create_combined_features(self, job_df):
        """Create weighted combination of job features for better matching"""
        job_df = job_df.copy()
        
        # Process all text columns
        job_df['title_processed'] = job_df['title'].apply(self.preprocess_text)
        job_df['description_processed'] = job_df['description'].apply(self.preprocess_text)
        job_df['category_processed'] = job_df['category'].apply(self.preprocess_text)
        job_df['role_processed'] = job_df['role'].apply(self.preprocess_text)
        job_df['qualification_processed'] = job_df['qualification'].apply(self.preprocess_text)
        
        # Create weighted combination
        weights = {
            'title_processed': 3.0,             # Job title is very important
            'description_processed': 2.0,       # Job description contains detailed requirements
            'category_processed': 1.5,          # Category provides general field
            'role_processed': 2.0,              # Role indicates position level
            'qualification_processed': 2.5       # Qualifications are key for matching
        }
        
        # Initialize combined features column
        job_df['combined_features'] = ''
        
        # Apply weights by repeating text
        for col, weight in weights.items():
            if col in job_df.columns:
                if weight > 1:
                    repeated_text = job_df[col].apply(lambda x: ' '.join([str(x)] * int(weight)))
                    job_df['combined_features'] += ' ' + repeated_text
                else:
                    job_df['combined_features'] += ' ' + job_df[col].astype(str)
        
        # Clean up the combined features
        job_df['combined_features'] = job_df['combined_features'].str.strip()
        
        return job_df
    
    def fit(self, jobs_data):
        """Fit the recommendation model on job postings data"""
        # Convert jobs_data to a DataFrame if it's not already
        if not isinstance(jobs_data, pd.DataFrame):
            # Create DataFrame from list of job objects
            job_df = pd.DataFrame([{
                'id': job.id,
                'title': job.title,
                'description': job.description,
                'category': job.category,
                'subcategory': job.subcategory,
                'role': job.role,
                'location': job.location,
                'company_name': job.company.name,
                'qualification': job.qualification,
                'salary': job.salary,
                'job_type': job.job_type
            } for job in jobs_data])
        else:
            job_df = jobs_data.copy()
        
        # Ensure all required columns exist
        for col in ['title', 'description', 'category', 'role']:
            if col not in job_df.columns:
                job_df[col] = ''
        
        # Fill NaN values
        job_df = job_df.fillna('')
        
        # Create combined features
        job_df = self.create_combined_features(job_df)
        
        # Create and fit TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.85,
            sublinear_tf=True
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(job_df['combined_features'])
        self.job_dataframe = job_df
        
        return self
    
    def get_recommendations_for_graduate(self, graduate, top_n=5):
        """Get job recommendations for a graduate based on their profile"""
        if self.tfidf_matrix is None or self.job_dataframe is None:
            raise ValueError("Model not fitted. Call fit() first with job data.")
        
        # Create a more comprehensive profile representation
        profile_parts = []
        if graduate.skills:
            profile_parts.append(graduate.skills)
        if graduate.experience:
            profile_parts.append(graduate.experience)
        if graduate.location_preference:
            profile_parts.append(graduate.location_preference)
            
        # If no profile information is available, return empty list
        if not profile_parts:
            return []
            
        graduate_profile = " ".join(profile_parts)
        
        # Preprocess the graduate profile text
        processed_profile = self.preprocess_text(graduate_profile)
        
        # Transform the graduate profile into TF-IDF space
        graduate_vector = self.vectorizer.transform([processed_profile])
        
        # Calculate cosine similarities
        cosine_similarities = cosine_similarity(graduate_vector, self.tfidf_matrix).flatten()
        
        # Get indices of top matches with non-zero similarity
        top_indices = cosine_similarities.argsort()[:-top_n-1:-1]
        
        # Filter out zero similarity matches
        recommendations = []
        for idx in top_indices:
            similarity_score = cosine_similarities[idx]
            if similarity_score > 0:
                job_id = self.job_dataframe.iloc[idx]['id']
                recommendations.append({
                    'job_id': job_id,
                    'similarity_score': float(similarity_score * 100)  # Convert to percentage
                })
        
        return recommendations
    
    def get_similarity_between_job_and_graduate(self, job_id, graduate):
        """Calculate similarity score between a specific job and a graduate"""
        if self.tfidf_matrix is None or self.job_dataframe is None:
            raise ValueError("Model not fitted. Call fit() first with job data.")
        
        # Find the job in the dataframe
        job_idx = self.job_dataframe[self.job_dataframe['id'] == job_id].index
        
        if len(job_idx) == 0:
            return 0.0  # Job not found
        
        job_idx = job_idx[0]
        
        # Create a profile representation for the graduate
        graduate_profile = f"{graduate.skills} {graduate.experience}"
        
        # Add location preference if available
        if graduate.location_preference:
            graduate_profile += f" {graduate.location_preference}"
        
        # Preprocess the graduate profile text
        processed_profile = self.preprocess_text(graduate_profile)
        
        # Transform the graduate profile into TF-IDF space
        graduate_vector = self.vectorizer.transform([processed_profile])
        
        # Get the job vector
        job_vector = self.tfidf_matrix[job_idx]
        
        # Calculate cosine similarity
        similarity = cosine_similarity(graduate_vector, job_vector.reshape(1, -1))[0][0]
        
        return similarity