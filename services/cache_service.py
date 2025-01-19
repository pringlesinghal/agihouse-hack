import pandas as pd
import os
import hashlib
import json
from datetime import datetime

class CacheService:
    def __init__(self, cache_file='cache/analysis_cache.csv'):
        self.cache_dir = os.path.dirname(cache_file)
        self.cache_file = cache_file
        self._ensure_cache_exists()

    def _ensure_cache_exists(self):
        """Ensure cache directory and file exist."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        if not os.path.exists(self.cache_file):
            # Create empty DataFrame with required columns
            df = pd.DataFrame(columns=[
                'timestamp',
                'query_hash',
                'segment_name',
                'segment_key',
                'detailed_analysis',
                'revenue_analysis',
                'persona',
                'value_proposition'
            ])
            df.to_csv(self.cache_file, index=False)

    def _generate_segment_key(self, segment_name, value_proposition):
        """Generate a unique but consistent key for a segment."""
        # Combine segment name and value proposition to create a unique identifier
        combined = f"{segment_name}:{value_proposition}"
        # Create a hash that will be consistent for the same input
        hash_obj = hashlib.md5(combined.encode())
        # Take first 8 characters of hash for a shorter but still unique key
        return hash_obj.hexdigest()[:8]

    def cache_analysis(self, query_input, segments_data, personas):
        """Cache the analysis results."""
        # Generate query hash
        query_hash = hashlib.md5(str(query_input).encode()).hexdigest()[:8]
        
        # Create new cache entries
        cache_entries = []
        
        # Split segments and process each one
        segments = segments_data['segments'].split('[')[1::2]  # Skip empty strings and value props
        
        for segment in segments:
            try:
                # Extract segment information
                segment_name = segment.split(']')[0].strip()
                
                # Get value proposition (text between last set of square brackets)
                value_prop_start = segment.rfind('[')
                value_prop_end = segment.rfind(']')
                value_proposition = ""
                if value_prop_start != -1 and value_prop_end != -1:
                    value_proposition = segment[value_prop_start+1:value_prop_end].strip()
                
                # Get main content (between segment name and value proposition)
                main_content = segment.split(']')[1]
                if value_prop_start != -1:
                    main_content = main_content[:value_prop_start].strip()
                
                # Generate segment key
                segment_key = self._generate_segment_key(segment_name, value_proposition)
                
                # Create cache entry
                cache_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'query_hash': query_hash,
                    'segment_name': segment_name,
                    'segment_key': segment_key,
                    'detailed_analysis': main_content,
                    'revenue_analysis': segments_data.get('grounding_data', ''),
                    'persona': personas.get(segment_name, ''),
                    'value_proposition': value_proposition
                }
                
                cache_entries.append(cache_entry)
                
            except Exception as e:
                print(f"Error processing segment {segment_name}: {str(e)}")
                continue
        
        # Create DataFrame from new entries
        new_df = pd.DataFrame(cache_entries)
        
        # Save to CSV (overwrite existing)
        new_df.to_csv(self.cache_file, index=False)
        
        return {segment['segment_key']: segment for segment in cache_entries}

    def get_cached_persona(self, segment_key):
        """Retrieve a cached persona by segment key."""
        try:
            df = pd.read_csv(self.cache_file)
            persona_row = df[df['segment_key'] == segment_key]
            if not persona_row.empty:
                return persona_row.iloc[0].to_dict()
            return None
        except Exception as e:
            print(f"Error retrieving cached persona: {str(e)}")
            return None

    def get_all_personas(self):
        """Retrieve all cached personas."""
        try:
            df = pd.read_csv(self.cache_file)
            return df.to_dict('records')
        except Exception as e:
            print(f"Error retrieving all personas: {str(e)}")
            return []
