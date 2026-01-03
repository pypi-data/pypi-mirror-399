from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.filedatalake import FileSystemClient
from azure.core.paging import ItemPaged
import pandas as pd
import io
import os

def _dataframe_to_adls_gen2_parquet_file(df: pd.DataFrame, access_token: str, destination_container: str, blob_directory: str, blob_name: str, sa_name: str) -> dict[str, any]:
    """
    Converts a pandas DataFrame to a Parquet file and uploads it to Azure Data Lake Storage Gen2.

    This function takes a pandas DataFrame, converts it to a Parquet file, and then uploads
    the file to a specified location in Azure Data Lake Storage Gen2 using the provided
    credential and container information.

    Args:
        df (pd.DataFrame): The pandas DataFrame to be converted and uploaded.
        access_token (str): The service principal access token for the Azure Storage account.
        destination_container (str): The name of the container in ADLS Gen2 where the file will be uploaded.
        blob_directory (str): The directory path within the container where the file will be stored.
        blob_name (str): The name of the blob (file) to be created in ADLS Gen2.

    Returns:
        dict[str, any]: A dictionary containing metadata about the uploaded blob, as returned by the upload_blob method.
        """

    blob = BlobClient(
        account_url=f"https://{sa_name}.blob.core.windows.net/", container_name=destination_container, blob_name=f"{blob_directory}{blob_name}", credential=access_token)
    if blob.exists():
        blob.delete_blob()
    df.to_parquet(blob_name, index=False, engine="fastparquet")
    with open(blob_name, "rb") as data:
        blob_result = blob.upload_blob(data) #, overwrite=True
    os.remove(blob_name)
    return blob_result


def _read_parquet_file_as_dataframe(file_path: str, container_system: FileSystemClient) -> pd.DataFrame:
    """
    Reads a Parquet file from Azure Data Lake Storage Gen2 and returns it as a pandas DataFrame.

    This function retrieves a Parquet file from the specified path in an ADLS Gen2 container,
    downloads its content, and converts it into a pandas DataFrame.

    Args:
        file_path (str): The path to the Parquet file within the ADLS Gen2 container.
        container_system (FileSystemClient): An instance of FileSystemClient representing
                                             the ADLS Gen2 file system.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the data from the Parquet file.
    """
    
    file_client = container_system.get_file_client(file_path)
    download = file_client.download_file()
    file_content = download.readall()
    buffer = io.BytesIO(file_content)
    data_frame = pd.read_parquet(buffer, engine="fastparquet")
    return data_frame


def _load_file_as_dataframe(file_path: ItemPaged | str,
                            container_system: FileSystemClient) -> pd.DataFrame:
    """
    Load a parquet file from the Azure Data Lake Storage (ADLS) Gen 2 storage as a pandas DataFrame.

    Parameters:
    file_path (ItemPaged | str): The path of the file in the ADLS.
    container_system (FileSystemClient): The Azure file system client used to access the file.

    Returns:
    pd.DataFrame: The contents of the file as a pandas DataFrame. 
    Returns an empty DataFrame if the file path is a directory.
    """

    data_frame = pd.DataFrame()
    if isinstance(file_path, str):
        data_frame = _read_parquet_file_as_dataframe(
            file_path, container_system)
    else:
        data_frame = _read_parquet_file_as_dataframe(
            file_path.name, container_system)

    return data_frame


def combine_files_in_directory_as_dataframe(path_to_files: str, container_name: str, access_token: str, sa_name: str) -> pd.DataFrame:
    """
    Combines parquet files from a specified path within a container into a single DataFrame.

    This function connects to an Azure Data Lake Storage container, retrieves the paths to the Parquet files in the specified directory,
    loads them into DataFrames, and combines them into a single DataFrame.

    Args:
        path_to_files (str): The path within the container where the Parquet files are stored.
        container_name (str): The name of the container in the Azure Data Lake Storage.

    Returns:
        pd.DataFrame: A DataFrame containing the combined data from all the Parquet files.
        return None if there are no files.

    Raises:
        Exception: If there is an issue connecting to the container or reading the files.
    """
    print(access_token, container_name, sa_name)
    container_system = FileSystemClient(account_url=f"https://{sa_name}.dfs.core.windows.net/",
                                                                file_system_name=container_name, credential=access_token)
    
    
    paths = container_system.get_paths()
    try:
        container_system = FileSystemClient(account_url=f"https://{sa_name}.dfs.core.windows.net/",
                                                                   file_system_name=container_name, credential=access_token)
        
        
        paths = container_system.get_paths(path_to_files)
        data_frames = []
        for file_path in paths:

            data_frame = _load_file_as_dataframe(file_path, container_system)
            data_frames.append(data_frame)
        combined_df = pd.concat(data_frames, ignore_index=True)
        print("Files loaded as DataFrame.")
        return combined_df
    except Exception as e:
        print(f"No files. {e}")
        return None
