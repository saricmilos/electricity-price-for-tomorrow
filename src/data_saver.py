from pathlib import Path
import pandas as pd

def save_dataframe_to_csv(df, 
                          filename, 
                          folder="Data", 
                          project_root=None, 
                          index=False, 
                          sep=',', 
                          encoding='utf-8',
                          create_dirs=True):
    """
    Save a pandas DataFrame to a CSV file, relative to the project root.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame to save.
    filename : str
        Name of the CSV file (e.g., 'energy.csv').
    folder : str or Path, default 'Data'
        Folder inside the project root where the file will be saved.
    project_root : Path, default None
        Root of the project. If None, will assume one level up from current working directory.
    index : bool, default False
        Whether to write row names (index).
    sep : str, default ','
        Field delimiter for the CSV file.
    encoding : str, default 'utf-8'
        Encoding of the CSV file.
    create_dirs : bool, default True
        Whether to create directories if they do not exist.
    
    Returns:
    --------
    Path
        Path to the saved CSV file.
    """
    if project_root is None:
        # Go up one level (assuming called from notebooks folder)
        project_root = Path.cwd().parent
    
    # Ensure folder is a Path object
    folder_path = Path(folder)
    full_path = project_root / folder_path / filename
    
    if create_dirs:
        full_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(full_path, index=index, sep=sep, encoding=encoding)
    print(f"DataFrame saved successfully to {full_path}")
    
    return full_path
