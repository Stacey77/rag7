"""
Garment Processing Module
Handles garment digitization and metadata
"""

class GarmentProcessor:
    def __init__(self):
        """Initialize garment processor"""
        # Load available garments database
        self.garments_db = self._initialize_garments()
    
    def _initialize_garments(self):
        """Initialize sample garments for MVP"""
        return [
            {
                'id': 'dress_001',
                'name': 'Summer Floral Dress',
                'category': 'dress',
                'brand': 'StyleBrand',
                'price': 89.99,
                'sizes': ['XS', 'S', 'M', 'L', 'XL'],
                'colors': ['Blue', 'Red', 'Green'],
                'material': 'Cotton',
                'image_url': '/assets/dress_001.png',
                'description': 'Lightweight summer dress with floral pattern'
            },
            {
                'id': 'shirt_001',
                'name': 'Classic White Shirt',
                'category': 'shirt',
                'brand': 'StyleBrand',
                'price': 49.99,
                'sizes': ['S', 'M', 'L', 'XL'],
                'colors': ['White', 'Blue', 'Black'],
                'material': 'Cotton Blend',
                'image_url': '/assets/shirt_001.png',
                'description': 'Professional white button-up shirt'
            },
            {
                'id': 'jeans_001',
                'name': 'Slim Fit Jeans',
                'category': 'pants',
                'brand': 'DenimCo',
                'price': 79.99,
                'sizes': ['28', '30', '32', '34', '36'],
                'colors': ['Blue', 'Black', 'Gray'],
                'material': 'Denim',
                'image_url': '/assets/jeans_001.png',
                'description': 'Modern slim fit jeans'
            },
            {
                'id': 'jacket_001',
                'name': 'Leather Jacket',
                'category': 'outerwear',
                'brand': 'UrbanStyle',
                'price': 199.99,
                'sizes': ['S', 'M', 'L', 'XL'],
                'colors': ['Black', 'Brown'],
                'material': 'Leather',
                'image_url': '/assets/jacket_001.png',
                'description': 'Classic leather jacket'
            },
            {
                'id': 'skirt_001',
                'name': 'Pleated Midi Skirt',
                'category': 'skirt',
                'brand': 'ChicWear',
                'price': 59.99,
                'sizes': ['XS', 'S', 'M', 'L'],
                'colors': ['Black', 'Navy', 'Burgundy'],
                'material': 'Polyester',
                'image_url': '/assets/skirt_001.png',
                'description': 'Elegant pleated midi skirt'
            }
        ]
    
    def get_available_garments(self):
        """Get all available garments"""
        return self.garments_db
    
    def get_garment_by_id(self, garment_id):
        """Get specific garment by ID"""
        for garment in self.garments_db:
            if garment['id'] == garment_id:
                return garment
        return None
    
    def filter_garments(self, category=None, size=None, color=None):
        """Filter garments by criteria"""
        filtered = self.garments_db
        
        if category:
            filtered = [g for g in filtered if g['category'] == category]
        
        if size:
            filtered = [g for g in filtered if size in g['sizes']]
        
        if color:
            filtered = [g for g in filtered if color in g['colors']]
        
        return filtered
