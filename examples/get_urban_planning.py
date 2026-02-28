#%% setup
from owslib.wms import WebMapService


def get_wms_metadata():
    # URL of the IDECanarias Planeamiento WMS
    url = "https://idecan2.grafcan.es/ServicioWMS/Planeamiento"

    print(f"Connecting to WMS service at: {url}...\n")

    # Connect to the WMS (using version 1.3.0, which is standard for modern WMS)
    wms = WebMapService(url, version='1.3.0')

    # 1. Retrieve Service-Level Metadata
    print("--- Service Metadata ---")
    print(f"Title: {wms.identification.title}")
    print(f"Abstract: {wms.identification.abstract}")
    print(f"Provider: {wms.provider.name}")
    print(f"Keywords: {', '.join(wms.identification.keywords)}")

    # 2. Retrieve Layer-Level Metadata for 'CLA'
    #layer_name = 'CLA'
    layer_name = 'CLASI'

    if layer_name in wms.contents:
        layer = wms.contents[layer_name]

        print(f"\n--- Layer Metadata: {layer_name} ---")
        print(f"Title: {layer.title}")
        print(f"Abstract: {layer.abstract}")

        # Check for Metadata URLs (this often contains the PDF or XML with the acronym dictionary)
        print("\n--- Metadata URLs (Check here for acronym mappings) ---")
        if layer.metadataUrls:
            for m in layer.metadataUrls:
                print(f"Type: {m.get('type')}, URL: {m.get('url')}")
        else:
            print("No external metadata URLs provided by the service.")

        # Check for Styles and Legend Graphics
        print("\n--- Styles & Legend (Visual acronym mappings) ---")
        if layer.styles:
            for style_name, style_info in layer.styles.items():
                print(f"Style Name: {style_name}")
                if 'legend' in style_info:
                    print(f"Legend URL: {style_info['legend']}")
                else:
                    print("No Legend URL available for this style.")
        else:
            print("No styles found.")

    else:
        print(f"\nLayer '{layer_name}' not found in the service.")
        print("Available layers:")
        for name in list(wms.contents)[:5]:  # Print first 5 as a sample
            print(f" - {name}")
        print(" ...")

#%% run
if __name__ == "__main__":
    get_wms_metadata()