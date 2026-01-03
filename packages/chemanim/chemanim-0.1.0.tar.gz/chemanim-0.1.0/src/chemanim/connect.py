import requests
import os

def fetch_pdb_file(pdb_id, download_dir=None):
    """
    Downloads PDB file from RCSB.
    
    Args:
        pdb_id (str): 4-character PDB code
        download_dir (str, optional): Directory to save to. Defaults to current directory.
        
    Returns:
        str: Path to downloaded file, or None if failed.
    """
    pdb_id = pdb_id.lower()
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    
    if download_dir:
        os.makedirs(download_dir, exist_ok=True)
        filename = os.path.join(download_dir, f"{pdb_id}.pdb")
    else:
        filename = f"{pdb_id}.pdb"
        
    if os.path.exists(filename):
        return filename
        
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print(f"Error fetching PDB {pdb_id}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching PDB {pdb_id}: {e}")
        return None
