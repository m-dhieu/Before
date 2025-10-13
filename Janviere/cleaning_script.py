"""
Tasks:
1. Load the train dataset (CSV)

2. Handle missing values, duplicates, invalid records, and outliers

3. Normalize and format timestamps, coordinates, and numeric fields

4. Define and justify at least three derived features (e.g., trip speed, idle time, fare per km)

5. Log excluded or suspicious records for transparency
"""

import pandas as pd      #this will help in loading and cleaning the data
import numpy as np       # this one too will has numerical operation will also help in finding missing values 
from datetime import datetime  # this will deal with date and time, this also can be essential in cleaning and transforming date columns   
import warnings           #during data operation this can help in controlling warning messages 
import math               # offers mathematical operations 
import os                 # file system operations for saving outputs


class TrainDataCleaner:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.original_shape = None
        self.cleaning_log = []
        self.invalid_records = None
        self.capped_records = None
        self.removed_missing_records = None
        self.removed_exact_duplicates = None
        self.removed_id_duplicates = None

    def load_data(self):
        # Loads the dataset
        print("Loading train dataset...")
        self.df = pd.read_csv(self.filepath)
        self.original_shape = self.df.shape # .shape it a special attribute of dataframe that returns size of loaded data in tuple
        print(f"Original train dataset shape: {self.original_shape}")
        self.log_step(f"Original train dataset loaded: {self.original_shape[0]} rows, {self.original_shape[1]} columns")
        return self
    def log_step(self, message):
          # Log cleaning steps
          self.cleaning_log.append(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
          print(message)

    def basic_info(self):
          # Dispaly basic info about train dataset
          print("\nTRAIN DATASET OVERVIEW: \n")
          print(f"\nDataset shape: {self.df.shape}")
          print(f"\nColumn types:")
          print(self.df.dtypes)
          print(f"\nMemory usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
          print(f"\nFirst few rows:")
          print(self.df.head())

          return self
    def check_missing_values(self):
          print("\nMISSING VALUES ANALYSIS")
          missing = self.df.isnull().sum()
          missing_pct = (missing / len(self.df)) * 100

          missing_df = pd.DataFrame({
            'Column': missing.index,
            'Missing_Count': missing.values,
            'Missing_Percentage': missing_pct.values
        })
        
          missing_df = missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)
        
          if len(missing_df) > 0:
            print("Missing values found:")
            print(missing_df)
          else:
            print("No missing values found!")
            
          self.log_step(f"Missing values check completed")
          return self
    
    def handle_missing_values(self):
        print("\nHANDLING MISSING VALUES")

        initial_rows = len(self.df)
        
        # Remove rows with any missing values (since all columns are important for train trips)
        try:
            missing_mask = self.df.isnull().any(axis=1)
            self.removed_missing_records = self.df[missing_mask].copy()
        except Exception:
            self.removed_missing_records = None
        self.df = self.df.dropna()
        
        rows_removed = initial_rows - len(self.df)
        if rows_removed > 0:
            self.log_step(f"Removed {rows_removed} rows with missing values")
        else:
            self.log_step("No missing values to handle")
            
        return self
    
    def check_duplicates(self):
        print("\nDUPLICATE ANALYSIS")
    
        # Check for exact duplicates
        exact_duplicates = self.df.duplicated().sum()
        print(f"Exact duplicate rows: {exact_duplicates}")
        
        # Check for duplicate trip IDs
        id_duplicates = self.df['id'].duplicated().sum()
        print(f"Duplicate trip IDs: {id_duplicates}")
        
        # Check for potential duplicate trips (same pickup/dropoff times and locations)
        trip_duplicates = self.df.duplicated(subset=['pickup_datetime', 'dropoff_datetime', 
                                                   'pickup_longitude', 'pickup_latitude',
                                                   'dropoff_longitude', 'dropoff_latitude']).sum()
        print(f"Potential duplicate trips: {trip_duplicates}")
        
        self.log_step("Duplicate analysis completed")
        return self
    
    def remove_duplicates(self):
        # Remove duplicate records
        print("\nREMOVING DUPLICATES")
        
        initial_rows = len(self.df)
        
        # Remove exact duplicates
        try:
            exact_removed_mask = self.df.duplicated(keep='first')
            self.removed_exact_duplicates = self.df[exact_removed_mask].copy()
        except Exception:
            self.removed_exact_duplicates = None
        self.df = self.df.drop_duplicates()
        exact_removed = initial_rows - len(self.df)
        
        # Remove duplicate IDs (keep first occurrence)
        initial_rows = len(self.df)
        try:
            id_removed_mask = self.df.duplicated(subset=['id'], keep='first')
            self.removed_id_duplicates = self.df[id_removed_mask].copy()
        except Exception:
            self.removed_id_duplicates = None
        self.df = self.df.drop_duplicates(subset=['id'])
        id_removed = initial_rows - len(self.df)
        
        if exact_removed > 0:
            self.log_step(f"Removed {exact_removed} exact duplicate rows")
        if id_removed > 0:
            self.log_step(f"Removed {id_removed} rows with duplicate IDs")
        if exact_removed == 0 and id_removed == 0:
            self.log_step("No duplicates to remove")
            
        return self
    
    def parse_datetime_columns(self):
        # Parse datetime columns
        print("\nPARSING DATETIME COLUMNS")

        try:
            self.df['pickup_datetime'] = pd.to_datetime(self.df['pickup_datetime'])
            self.df['dropoff_datetime'] = pd.to_datetime(self.df['dropoff_datetime'])
            self.log_step("Successfully parsed datetime columns")
        except Exception as e:
            print(f"Error parsing datetime columns: {e}")
            
        return self
    
    
    def validate_data_integrity(self):
        # Check for invalid records
        print("\nDATA INTEGRITY VALIDATION")
        
        initial_rows = len(self.df)
        issues_found = []
        
        # Check for negative or zero trip duration
        invalid_duration = self.df['trip_duration'] <= 0
        issues_found.append(f"Invalid trip duration (<=0): {invalid_duration.sum()}")
        
        # Check for trips where dropoff is before pickup
        invalid_time_order = self.df['dropoff_datetime'] <= self.df['pickup_datetime']
        issues_found.append(f"Invalid time order (dropoff <= pickup): {invalid_time_order.sum()}")
        
        # Check for invalid passenger counts
        invalid_passengers = (self.df['passenger_count'] <= 0) | (self.df['passenger_count'] > 8)
        issues_found.append(f"Invalid passenger count: {invalid_passengers.sum()}")
        
        # Check for invalid coordinates 
        invalid_pickup_lat = (self.df['pickup_latitude'] < 40.4) | (self.df['pickup_latitude'] > 41.0)
        invalid_pickup_lon = (self.df['pickup_longitude'] < -74.3) | (self.df['pickup_longitude'] > -73.7)
        invalid_dropoff_lat = (self.df['dropoff_latitude'] < 40.4) | (self.df['dropoff_latitude'] > 41.0)
        invalid_dropoff_lon = (self.df['dropoff_longitude'] < -74.3) | (self.df['dropoff_longitude'] > -73.7)
        
        invalid_coords = invalid_pickup_lat | invalid_pickup_lon | invalid_dropoff_lat | invalid_dropoff_lon
        issues_found.append(f"Invalid coordinates: {invalid_coords.sum()}")
        
        # Check for zero coordinates (likely missing/invalid)
        zero_coords = ((self.df['pickup_latitude'] == 0) | (self.df['pickup_longitude'] == 0) |
                      (self.df['dropoff_latitude'] == 0) | (self.df['dropoff_longitude'] == 0))
        issues_found.append(f"Zero coordinates: {zero_coords.sum()}")
        
        for issue in issues_found:
            print(f"  {issue}")
            
        # Combine all invalid conditions
        invalid_rows = (invalid_duration | invalid_time_order | invalid_passengers | 
                       invalid_coords | zero_coords)
        
        # Store invalid rows for transparency before removal
        try:
            self.invalid_records = self.df[invalid_rows].copy()
        except Exception:
            self.invalid_records = None

        self.df = self.df[~invalid_rows]
        rows_removed = initial_rows - len(self.df)
        
        if rows_removed > 0:
            self.log_step(f"Removed {rows_removed} invalid records")
        else:
            self.log_step("No invalid records found")
            
        return self
    
    def detect_outliers(self):
        # Detect outliers using IQR method
        """
        IQR method:
        a statistical measure that describes the spread of the middle 50% of a dataset.
        """
        print("\nOUTLIER DETECTION")
        
        # Focus on key numerical columns for outlier detection
        numerical_cols = ['trip_duration', 'passenger_count']
        
        outlier_info = {}
        
        for col in numerical_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound))
            outlier_count = outliers.sum()
            outlier_pct = (outlier_count / len(self.df)) * 100
            
            outlier_info[col] = {
                'count': outlier_count,
                'percentage': outlier_pct,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
            
            print(f"\n{col}:")
            print(f"  Outliers: {outlier_count} ({outlier_pct:.2f}%)")
            print(f"  Bounds: [{lower_bound:.2f}, {upper_bound:.2f}]")
            print(f"  Range: [{self.df[col].min():.2f}, {self.df[col].max():.2f}]")
        
        self.outlier_info = outlier_info
        self.log_step("Outlier detection completed")
        return self
    
    def handle_outliers(self, method='cap'):
        # Handle outliers using specified method
        print(f"\nHANDLING OUTLIERS (Method: {method.upper()})")
    
        initial_rows = len(self.df)
        
        if method == 'remove':
            # Remove extreme outliers for trip_duration only
            Q1 = self.df['trip_duration'].quantile(0.01)  # More conservative
            Q3 = self.df['trip_duration'].quantile(0.99)
            
            self.df = self.df[(self.df['trip_duration'] >= Q1) & 
                             (self.df['trip_duration'] <= Q3)]
            
            rows_removed = initial_rows - len(self.df)
            self.log_step(f"Removed {rows_removed} extreme outliers")
            
        elif method == 'cap':
            # Cap extreme values for trip_duration
            Q1 = self.df['trip_duration'].quantile(0.01)
            Q99 = self.df['trip_duration'].quantile(0.99)
            
            original_min = self.df['trip_duration'].min()
            original_max = self.df['trip_duration'].max()
            
            # Record rows that will be capped for transparency
            try:
                original_td = self.df['trip_duration'].copy()
                capped_low_mask = original_td < Q1
                capped_high_mask = original_td > Q99
                capped_mask = capped_low_mask | capped_high_mask
                if capped_mask.any():
                    capped_df = self.df.loc[capped_mask, :].copy()
                    capped_df['trip_duration_original'] = original_td.loc[capped_mask]
                    capped_df['trip_duration_capped'] = np.clip(original_td.loc[capped_mask], Q1, Q99)
                    self.capped_records = capped_df
                else:
                    self.capped_records = None
            except Exception:
                self.capped_records = None

            self.df['trip_duration'] = np.clip(self.df['trip_duration'], Q1, Q99)
            
            self.log_step(f"Capped trip_duration values to range [{Q1:.0f}, {Q99:.0f}] seconds")
            
        return self
    
    def normalize_data(self):
        # Normalize and format timestamps, coordinates, and numeric fields
        print("\nDATA NORMALIZATION")
        
        # Normalize timestamps to consistent format
        self.df['pickup_datetime'] = pd.to_datetime(self.df['pickup_datetime'])
        self.df['dropoff_datetime'] = pd.to_datetime(self.df['dropoff_datetime'])
        
        # Round coordinates to reasonable precision (6 decimal places)
        coord_cols = ['pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude']
        for col in coord_cols:
            self.df[col] = self.df[col].round(6)
        
        # Ensure passenger_count is integer
        self.df['passenger_count'] = self.df['passenger_count'].astype(int)
        
        # Ensure trip_duration is integer
        self.df['trip_duration'] = self.df['trip_duration'].astype(int)
        
        # Normalize vendor_id to categorical
        self.df['vendor_id'] = self.df['vendor_id'].astype('category')
        
        # Normalize store_and_fwd_flag to categorical
        self.df['store_and_fwd_flag'] = self.df['store_and_fwd_flag'].astype('category')
        
        self.log_step("Data normalization completed")
        return self
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        # Calculate Haversine distance between two points in kilometers
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        return c * r
    
    def create_derived_features(self):
        # Create derived features as required by assignment
        print("\nCREATING DERIVED FEATURES")
        
        # 1. Trip Distance (in kilometers)
        print("Creating trip distance feature...")
        self.df['trip_distance_km'] = self.df.apply(
            lambda row: self.calculate_distance(
                row['pickup_latitude'], row['pickup_longitude'],
                row['dropoff_latitude'], row['dropoff_longitude']
            ), axis=1
        )
        
        # 2. Trip Speed (km/h)
        print("Creating trip speed feature...")
        # Convert trip_duration from seconds to hours
        self.df['trip_duration_hours'] = self.df['trip_duration'] / 3600
        # Calculate speed, handling division by zero
        self.df['trip_speed_kmh'] = np.where(
            self.df['trip_duration_hours'] > 0,
            self.df['trip_distance_km'] / self.df['trip_duration_hours'],
            0
        )
        
        # 3. Trip Efficiency (distance per minute)
        print("Creating trip efficiency feature...")
        self.df['trip_efficiency'] = np.where(
            self.df['trip_duration'] > 0,
            self.df['trip_distance_km'] / (self.df['trip_duration'] / 60),  # km per minute
            0
        )
        
        # 4. Day of Week
        print("Creating temporal features...")
        self.df['pickup_day_of_week'] = self.df['pickup_datetime'].dt.day_name()
        self.df['pickup_hour'] = self.df['pickup_datetime'].dt.hour
        self.df['pickup_month'] = self.df['pickup_datetime'].dt.month
        
        # 5. Trip Duration Categories
        print("Creating trip duration categories...")
        self.df['trip_duration_category'] = pd.cut(
            self.df['trip_duration'],
            bins=[0, 300, 600, 1200, 1800, float('inf')],
            labels=['Very Short (0-5min)', 'Short (5-10min)', 'Medium (10-20min)', 
                   'Long (20-30min)', 'Very Long (30min+)']
        )
        
        # 6. Distance Categories
        print("Creating distance categories...")
        self.df['distance_category'] = pd.cut(
            self.df['trip_distance_km'],
            bins=[0, 1, 3, 5, 10, float('inf')],
            labels=['Very Short (0-1km)', 'Short (1-3km)', 'Medium (3-5km)', 
                   'Long (5-10km)', 'Very Long (10km+)']
        )
        
        # 7. Speed Categories
        print("Creating speed categories...")
        self.df['speed_category'] = pd.cut(
            self.df['trip_speed_kmh'],
            bins=[0, 10, 20, 30, 50, float('inf')],
            labels=['Very Slow (0-10km/h)', 'Slow (10-20km/h)', 'Normal (20-30km/h)', 
                   'Fast (30-50km/h)', 'Very Fast (50km/h+)']
        )

        # 8. Fare-based features (if fare data is available)
        if 'fare_amount' in self.df.columns:
            print("Creating fare-based features...")
            # Avoid division by zero when distance or duration is zero
            self.df['fare_per_km'] = np.where(
                self.df['trip_distance_km'] > 0,
                self.df['fare_amount'] / self.df['trip_distance_km'],
                np.nan
            )
            self.df['fare_per_min'] = np.where(
                self.df['trip_duration'] > 0,
                self.df['fare_amount'] / (self.df['trip_duration'] / 60.0),
                np.nan
            )
            if 'tip_amount' in self.df.columns:
                self.df['tip_percentage'] = np.where(
                    self.df['fare_amount'] > 0,
                    (self.df['tip_amount'] / self.df['fare_amount']) * 100.0,
                    np.nan
                )
        
        # Log feature creation
        self.log_step("Created derived features:")
        self.log_step("  - trip_distance_km: Haversine distance between pickup and dropoff")
        self.log_step("  - trip_speed_kmh: Average speed during trip")
        self.log_step("  - trip_efficiency: Distance covered per minute")
        self.log_step("  - pickup_day_of_week: Day of the week for pickup")
        self.log_step("  - pickup_hour: Hour of day for pickup")
        self.log_step("  - trip_duration_category: Categorical trip duration")
        self.log_step("  - distance_category: Categorical trip distance")
        self.log_step("  - speed_category: Categorical trip speed")
        if 'fare_amount' in self.df.columns:
            self.log_step("  - fare_per_km: Fare normalized by distance")
            self.log_step("  - fare_per_min: Fare normalized by minutes")
            if 'tip_amount' in self.df.columns:
                self.log_step("  - tip_percentage: Tip as percentage of fare")
        
        return self
    
    def validate_derived_features(self):
        # Validate the derived features for reasonableness
        print("\nVALIDATING DERIVED FEATURES")
        
        # Check for unreasonable values
        issues = []
        
        # Check for negative distances
        negative_distances = (self.df['trip_distance_km'] < 0).sum()
        if negative_distances > 0:
            issues.append(f"Negative distances: {negative_distances}")
        
        # Check for extremely high speeds (>200 km/h is unrealistic)
        unrealistic_speeds = (self.df['trip_speed_kmh'] > 200).sum()
        if unrealistic_speeds > 0:
            issues.append(f"Unrealistic speeds (>200 km/h): {unrealistic_speeds}")
        
        # Check for zero distance trips with non-zero duration
        zero_distance_trips = ((self.df['trip_distance_km'] == 0) & (self.df['trip_duration'] > 0)).sum()
        if zero_distance_trips > 0:
            issues.append(f"Zero distance trips with duration: {zero_distance_trips}")
        
        if issues:
            print("Issues found in derived features:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("All derived features validated successfully!")
        
        # Summary statistics
        print(f"\nDerived features summary:")
        print(f"Distance range: {self.df['trip_distance_km'].min():.3f} - {self.df['trip_distance_km'].max():.3f} km")
        print(f"Speed range: {self.df['trip_speed_kmh'].min():.2f} - {self.df['trip_speed_kmh'].max():.2f} km/h")
        print(f"Efficiency range: {self.df['trip_efficiency'].min():.3f} - {self.df['trip_efficiency'].max():.3f} km/min")
        
        self.log_step("Derived features validation completed")
        return self
    
    def create_summary_statistics(self):
        # Create summary statistics
        print("\nSUMMARY STATISTICS")
        
        numerical_cols = ['trip_duration', 'passenger_count', 'pickup_longitude', 
                         'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude']
        
        print("\nNumerical columns summary:")
        print(self.df[numerical_cols].describe())
        
        print("\nCategorical columns summary:")
        print(f"Vendor ID distribution:")
        print(self.df['vendor_id'].value_counts())
        
        print(f"\nStore and forward flag distribution:")
        print(self.df['store_and_fwd_flag'].value_counts())
        
        # Date range
        print(f"\nDate range:")
        print(f"From: {self.df['pickup_datetime'].min()}")
        print(f"To: {self.df['pickup_datetime'].max()}")
        
        return self
    
    def save_cleaned_data(self, output_path='train_cleaned.csv'):
        # Save cleaned dataset
        print("\nSAVING CLEANED DATA")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else '.'
        os.makedirs(output_dir, exist_ok=True)

        self.df.to_csv(output_path, index=False)
        
        print(f"Cleaned dataset saved to: {output_path}")
        print(f"Original shape: {self.original_shape}")
        print(f"Cleaned shape: {self.df.shape}")
        print(f"Rows removed: {self.original_shape[0] - self.df.shape[0]}")
        print(f"Reduction: {((self.original_shape[0] - self.df.shape[0]) / self.original_shape[0] * 100):.2f}%")
        
        self.log_step(f"Cleaned data saved: {self.df.shape[0]} rows remaining")
        
        # Save transparency logs alongside cleaned data
        self.save_transparency_logs(output_dir)
        return self

    def save_transparency_logs(self, output_dir):
        # Save logs for excluded or suspicious records
        try:
            if self.invalid_records is not None and len(self.invalid_records) > 0:
                invalid_path = os.path.join(output_dir, 'excluded_invalid_records.csv')
                self.invalid_records.to_csv(invalid_path, index=False)
                self.log_step(f"Saved invalid/excluded records to: {invalid_path}")
        except Exception as e:
            print(f"Failed to save invalid records log: {e}")

        try:
            if self.capped_records is not None and len(self.capped_records) > 0:
                capped_path = os.path.join(output_dir, 'capped_trip_durations.csv')
                self.capped_records.to_csv(capped_path, index=False)
                self.log_step(f"Saved capped outlier records to: {capped_path}")
        except Exception as e:
            print(f"Failed to save capped records log: {e}")

        try:
            if self.removed_missing_records is not None and len(self.removed_missing_records) > 0:
                missing_path = os.path.join(output_dir, 'removed_missing_rows.csv')
                self.removed_missing_records.to_csv(missing_path, index=False)
                self.log_step(f"Saved removed rows with missing values to: {missing_path}")
        except Exception as e:
            print(f"Failed to save missing rows log: {e}")

        try:
            if self.removed_exact_duplicates is not None and len(self.removed_exact_duplicates) > 0:
                exact_dups_path = os.path.join(output_dir, 'removed_exact_duplicates.csv')
                self.removed_exact_duplicates.to_csv(exact_dups_path, index=False)
                self.log_step(f"Saved removed exact duplicates to: {exact_dups_path}")
        except Exception as e:
            print(f"Failed to save exact duplicates log: {e}")

        try:
            if self.removed_id_duplicates is not None and len(self.removed_id_duplicates) > 0:
                id_dups_path = os.path.join(output_dir, 'removed_id_duplicates.csv')
                self.removed_id_duplicates.to_csv(id_dups_path, index=False)
                self.log_step(f"Saved removed duplicate IDs to: {id_dups_path}")
        except Exception as e:
            print(f"Failed to save id duplicates log: {e}")

        try:
            if hasattr(self, 'outlier_info') and isinstance(self.outlier_info, dict) and len(self.outlier_info) > 0:
                bounds_df = pd.DataFrame.from_dict(self.outlier_info, orient='index')
                bounds_df_path = os.path.join(output_dir, 'outlier_bounds.csv')
                bounds_df.to_csv(bounds_df_path)
                self.log_step(f"Saved outlier bounds to: {bounds_df_path}")
        except Exception as e:
            print(f"Failed to save outlier bounds log: {e}")
    
    def print_cleaning_summary(self):
        # Print summary of all cleaning steps
        print("\nCLEANING PROCESS SUMMARY")
        
        for step in self.cleaning_log:
            print(step)
            
        print(f"\nFinal Results:")
        print(f"Original dataset: {self.original_shape[0]} rows, {self.original_shape[1]} columns")
        print(f"Cleaned dataset: {self.original_shape[0]} rows, {self.original_shape[1]} columns")
        print(f"Data retention: {(self.df.shape[0] / self.original_shape[0] * 100):.2f}%")

    
    

                


def main():
        base_dir = os.path.dirname(__file__)
        input_csv = os.path.join(base_dir, 'train.csv')
        output_csv = os.path.join(base_dir, '..', 'processed', 'train_cleaned.csv')
        cleaner = TrainDataCleaner(input_csv)
        (cleaner
         .load_data()
         .basic_info()
         .check_missing_values()
         .handle_missing_values()
         .parse_datetime_columns()
         .check_duplicates()
         .remove_duplicates()
         .validate_data_integrity()
         .detect_outliers()         .handle_outliers(method='cap')
         .normalize_data()
         .create_derived_features()
         .validate_derived_features()
         .create_summary_statistics()
         .save_cleaned_data(output_csv)
         .print_cleaning_summary()
        #  .log_step("Train dataset loaded successfully!")
         
         

        )
    
if __name__ == "__main__":
        main()
