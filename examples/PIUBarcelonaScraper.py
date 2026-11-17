import requests
import json
import os

class PIUBarcelonaScraper:
    """
    Automates fetching urban planning history, qualifications, and encumbrances
    (afectacions urbanístiques) from Barcelona's Portal de Informació Urbanística (PIU).
    """
    BASE_URL = "https://piu.barcelona.cat"
    SEARCH_ENDPOINT = f"{BASE_URL}/piu/api/v1/cerca/referencia-cadastral"
    REPORT_ENDPOINT = f"{BASE_URL}/piu/api/v1/informe"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://piu.barcelona.cat/",
            "Accept-Language": "ca,es;q=0.9,en;q=0.8"
        })

    def fetch_cadastral_info(self, cadastral_ref: str) -> dict:
        """
        Retrieves raw JSON payload containing urban planning history, 
        encumbrances (afectacions), and zoning codes for a 20-character RC.
        """
        clean_rc = cadastral_ref.strip().upper()
        
        # Step 1: Query location & parcel internal ID from Cadastral Ref
        params = {"rc": clean_rc}
        response = self.session.get(self.SEARCH_ENDPOINT, params=params, timeout=15)
        
        if response.status_code == 404:
            raise ValueError(f"Cadastral reference '{clean_rc}' not found in Barcelona municipality.")
        response.raise_for_status()
        
        search_results = response.json()
        
        # Step 2: Fetch detailed urban planning report (Informe Urbanístic)
        parcel_id = search_results.get("idParcela") or search_results.get("id")
        if not parcel_id:
            return search_results

        report_response = self.session.get(f"{self.REPORT_ENDPOINT}/{parcel_id}", timeout=15)
        report_response.raise_for_status()
        
        return report_response.json()

    def download_pdf_report(self, cadastral_ref: str, output_dir: str = ".") -> str:
        """
        Downloads the official urbanistic report PDF for the given parcel.
        """
        clean_rc = cadastral_ref.strip().upper()
        pdf_url = f"{self.BASE_URL}/piu/api/v1/informe/pdf/{clean_rc}"
        
        response = self.session.get(pdf_url, stream=True, timeout=30)
        response.raise_for_status()

        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"PIU_Report_{clean_rc}.pdf")
        
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return file_path


if __name__ == "__main__":
    # Example 20-character Barcelona Cadastral Reference
    CADASTRA_REF = "0800101DF2800A0001JK" 

    scraper = PIUBarcelonaScraper()

    try:
        print(f"Fetching PIU data for: {CADASTRA_REF}")
        data = scraper.fetch_cadastral_info(CADASTRA_REF)
        
        # Extract Key Information
        qualifications = data.get("qualificacions", [])
        affectations = data.get("afectacions", [])
        history_plans = data.get("planejaments", [])

        print(f"\n--- URBANISTIC STATUS ---")
        print(f"Zoning Qualifications: {len(qualifications)} found")
        print(f"Encumbrances/Affectations: {len(affectations)} found")
        print(f"Historical Planning Files: {len(history_plans)} found")

        # Save JSON output
        json_file = f"piu_{CADASTRA_REF}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\nSaved full report JSON to {json_file}")

        # Download Official PDF
        pdf_path = scraper.download_pdf_report(CADASTRA_REF)
        print(f"Downloaded PDF summary to {pdf_path}")

    except Exception as e:
        print(f"Error executing scraper: {e}")