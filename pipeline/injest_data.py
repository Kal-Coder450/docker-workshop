#!/usr/bin/env python
# coding: utf-8

import argparse
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

def run(params):
    # Unpack the command-line arguments
    year = int(params.year)
    month = int(params.month)
    
    # Hardcoded database parameters
    pg_user = 'root'
    pg_pass = 'root'
    pg_host = 'localhost'
    pg_port = 5432
    pg_db = 'ny_taxi'
    target_table = 'yellow_taxi_data'
    chunksize = 100000

    # Build the URL and engine connection string correctly using f-strings
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow'
    url = f'{prefix}/yellow_tripdata_{year:04d}-{month:02d}.csv.gz'
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    print(f"Connecting to database and fetching data from: {url}")

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize,
    )

    first = True

    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(0).to_sql(
                name=target_table, 
                con=engine, 
                if_exists='replace',
                index=False
            )
            first = False

        # Insert chunk with proper loop indentation
        df_chunk.to_sql(
            name=target_table, 
            con=engine, 
            if_exists='append',
            index=False
        )

if __name__ == '__main__':
    # Set up argparse to read variables from your terminal execution
    parser = argparse.ArgumentParser(description='Ingest CSV data to PostgreSQL')
    parser.add_argument('--year', required=True, help='Year of the data (e.g., 2021)')
    parser.add_argument('--month', required=True, help='Month of the data (e.g., 1)')
    
    args = parser.parse_args()
    run(args)
