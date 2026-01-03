from importlib import resources
import pandas as pd

# Start Function
def convert(zipCode):

    # Validate Input
    if not (len(zipCode) == 5 and zipCode.isdigit()):
        return False

    # Read in, using importlib due to filesystem challenges
    with resources.files("zipToCBSA.data").joinpath("zip-cbsa.csv").open("rb") as f:
        df = pd.read_csv(f)

    # Convert ZIP column to string & fill
    df['zip'] = df['zip'].astype(str).str.zfill(5)

    # Filter out matching rows & convert to a list of dictionaries
    df_sliced = df[df['zip'] == zipCode]
    CBSAResults = df_sliced.to_dict(orient='records')

    return CBSAResults
