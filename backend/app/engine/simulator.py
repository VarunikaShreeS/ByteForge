def generate_mock_app_store(brand_name: str, official_publisher: str) -> list:
    """Generates a list of apps found in the wild to test the detection engine."""
    return [
        {
            "app_name": "Candy Crush Saga",
            "publisher": "King",
            "description": "Match 3 puzzle game.",
            "icon_path": "candy_logo.png"
        },
        {
            "app_name": brand_name,
            "publisher": official_publisher,
            "description": f"The official mobile app for {brand_name}.",
            "icon_path": "official_logo.png"
        },
        {
            "app_name": f"{brand_name} Support Wallet",
            "publisher": "HackerGroup_01",
            "description": f"Urgent KYC verification for {brand_name}. DM for support.",
            "icon_path": "stolen_logo.png"
        }
    ]