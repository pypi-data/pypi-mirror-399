from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.filedatalake import FileSystemClient
from azure.core.paging import ItemPaged
import pandas as pd
import io
    
def load_existing_silver_curated_parquet(path_and_file_name: str, container_name: str, full_refresh: bool, access_token: str, sa_name: str) -> pd.DataFrame | None:
    """
    Load an existing Silver Curated Parquet file from the ADLS into a DataFrame.

    This function connects to Azure Blob Storage, retrieves a Parquet file specified by the path and filename, and loads it into
    a DataFrame. If a full refresh is requested, the function returns None to indicate no data should be loaded.

    Args:
        path_and_file_name (str): The full path and filename of the Parquet file within the container.
        container_name (str): The name of the container in the ADLS where the Parquet file is stored.
        full_refresh (bool): A flag indicating whether to perform a full refresh. If True, the function will return None.

    Returns:
        Optional[pd.DataFrame]: A DataFrame containing the data from the Parquet file if `full_refresh` is False.
        If `full_refresh` is True, returns None.
    """
    if full_refresh:
        print("Full refresh")
        return None
    blob_client = BlobClient(
        account_url=f"https://{sa_name}.blob.core.windows.net/",
        container_name=container_name,
        blob_name=path_and_file_name,
        credential=access_token
    )
    blob_data = blob_client.download_blob().readall()
    blob_df = pd.read_parquet(io.BytesIO(blob_data),engine="fastparquet")
    print("Incremental refresh: Silver curated file successfully loaded.")
    return blob_df

def combine_new_and_existing(column_for_comparison: str, new: pd.DataFrame | None, existing: pd.DataFrame | None) -> pd.DataFrame:
    """
    Combines the bronze new DataFrame with the existing silver curated DataFrame based on a specified column for comparison.

    This function performs the following steps:
    1. If the `new` DataFrame is `None`, it returns the `existing` DataFrame.
    2. If the `existing` DataFrame is `None`, it returns the `new` DataFrame.
    3. If both DataFrames are provided, it removes rows in the `existing` DataFrame that have corresponding values
       in the `new` DataFrame based on the `column_for_comparison`.
    4. It then concatenates the filtered `existing` DataFrame with the `new` DataFrame and returns the combined DataFrame.

    Args:
        column_for_comparison (str): The name of the column used to identify and compare rows between the DataFrames.
        new (pd.DataFrame | None): The new DataFrame to be combined with the existing DataFrame. May be `None`.
        existing (pd.DataFrame | None): The existing DataFrame to be combined with the new DataFrame. May be `None`.

    Returns:
        pd.DataFrame: A DataFrame that is the result of combining the `new` and `existing` DataFrames. Rows in the `existing`
                      DataFrame that are also present in the `new` DataFrame are removed before concatenation.
    """
    if new is None:
        return existing
    if existing is None:
        return new
    # ToDo: add comment.
    df_existing_not_in_new = existing[~existing[column_for_comparison].isin(new[column_for_comparison])]
    silver_curated = pd.concat([df_existing_not_in_new, new], ignore_index=True)
    return silver_curated

def move_files_from_new_to_processed(account_url: str, container: str, source_directory: str, destination_directory: str, access_token: str, sa_name: str) -> None:
    """
    Moves files from a source directory to a destination directory within an ADLS container.

    This function performs the following steps:
    1. Connects to the Azure Blob Storage service using a connection string.
    2. Lists all blobs in the specified source directory within the given container.
    3. For each blob, copies it from the source directory to the destination directory.
    4. Deletes the original blob from the source directory after the copy operation is complete.

    Args:
        account_url (str): The URL of the Azure Storage account. Used to construct the source blob path.
        container (str): The name of the container within the Azure Storage account where the blobs are located.
        source_directory (str): The directory within the container where the files are currently located. Should be a prefix used to filter blobs.
        destination_directory (str): The directory within the container where the files will be moved to. 

    Returns:
        None: This function does not return any value. It performs operations directly on Azure Blob Storage.
    """
    # ToDo: make sure it doesnt depend on a / in the source_directory.
    blob_service_client = BlobServiceClient(
        account_url=f"https://{sa_name}.blob.core.windows.net/",
        credential=access_token,
    )
    source_container_client = blob_service_client.get_container_client(container)
    blobs = source_container_client.list_blobs(name_starts_with=source_directory)
    for blob in blobs:
        source_blob_path = f"{account_url}/{container}/{blob.name}"
        print(blob.name)
        destination_blob_path = destination_directory + blob.name.split('/')[-1]
        blob_service_client.get_blob_client(container, destination_blob_path).start_copy_from_url(source_blob_path)
        blob_service_client.get_blob_client(container, blob.name).delete_blob()  
    print(f"Files moved successfully from {source_directory} to {destination_directory}!")