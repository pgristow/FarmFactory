"""
Column mapping service for intelligent column name matching.

Uses fuzzy matching to map source columns to target database fields.
"""
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
import re
import logging

logger = logging.getLogger(__name__)


class ColumnMapper:
    """
    Intelligent column mapping with fuzzy matching.

    Features:
    - Fuzzy string matching for column names
    - Support for multiple naming conventions (snake_case, camelCase, Title Case)
    - Confidence scoring
    - Alternative suggestions
    - Required field validation
    """

    # Define target schema for each data type
    COLUMN_SCHEMAS = {
        'farms_plots': {
            'required': ['farm_name', 'plot_name'],
            'optional': [
                'farm_address', 'latitude', 'longitude',
                'total_area_hectares', 'plot_area_hectares',
                'soil_type', 'crop_type'
            ],
        },
        'irrigation': {
            'required': ['farm_name', 'plot_name', 'irrigation_date', 'amount_liters'],
            'optional': [
                'duration_minutes', 'method', 'water_source',
                'flow_rate', 'notes'
            ],
        },
        'nutrients': {
            'required': ['farm_name', 'plot_name', 'application_date', 'nutrient_type'],
            'optional': [
                'amount_kg', 'method', 'concentration',
                'n_content', 'p_content', 'k_content', 'notes'
            ],
        },
        'phenology': {
            'required': ['farm_name', 'plot_name', 'observation_date', 'growth_stage'],
            'optional': [
                'plant_height_cm', 'leaf_count', 'flowering_percentage',
                'notes', 'image_url'
            ],
        },
        'financial': {
            'required': ['farm_name', 'plot_name', 'transaction_date', 'amount'],
            'optional': [
                'transaction_type', 'category', 'description',
                'quantity', 'unit', 'price_per_unit'
            ],
        },
    }

    # Common variations for column names
    COLUMN_ALIASES = {
        # Farm/Plot names
        'farm_name': ['farm', 'farm name', 'farmname', 'farm_id', 'farmid', 'farm id'],
        'plot_name': ['plot', 'plot name', 'plotname', 'field', 'field name', 'plot_id', 'plotid'],

        # Location
        'latitude': ['lat', 'latitude', 'lat.', 'y', 'y_coord'],
        'longitude': ['lon', 'lng', 'long', 'longitude', 'lon.', 'x', 'x_coord'],
        'farm_address': ['address', 'location', 'farm address', 'farm_location'],

        # Area
        'total_area_hectares': [
            'area', 'total area', 'hectares', 'ha', 'area_ha',
            'total_area', 'farm_area', 'size'
        ],
        'plot_area_hectares': [
            'plot area', 'plot_area', 'field area', 'area_ha',
            'plot size', 'field_size'
        ],

        # Dates
        'irrigation_date': [
            'date', 'irrigation date', 'watering date', 'event date',
            'date_time', 'datetime', 'timestamp'
        ],
        'application_date': [
            'date', 'application date', 'applied date', 'event date',
            'date_time', 'datetime', 'timestamp'
        ],
        'observation_date': [
            'date', 'observation date', 'obs date', 'recorded date',
            'date_time', 'datetime', 'timestamp'
        ],
        'transaction_date': [
            'date', 'transaction date', 'purchase date', 'sale date',
            'date_time', 'datetime', 'timestamp'
        ],

        # Irrigation
        'amount_liters': [
            'amount', 'water amount', 'volume', 'liters', 'litres',
            'water_volume', 'irrigation_amount', 'gallons', 'quantity'
        ],
        'duration_minutes': [
            'duration', 'time', 'minutes', 'irrigation time',
            'watering time', 'duration_min'
        ],
        'method': ['irrigation method', 'watering method', 'type'],
        'water_source': ['source', 'water source', 'supply'],

        # Nutrients
        'nutrient_type': [
            'nutrient', 'fertilizer', 'fertilizer type', 'type',
            'product', 'product_name'
        ],
        'amount_kg': [
            'amount', 'quantity', 'kg', 'kilograms', 'weight',
            'application_amount', 'lbs', 'pounds'
        ],
        'concentration': ['concentration', 'strength', 'dilution'],

        # Phenology
        'growth_stage': [
            'stage', 'growth stage', 'phenological stage', 'phase',
            'development_stage'
        ],
        'plant_height_cm': [
            'height', 'plant height', 'height_cm', 'cm',
            'plant_height_cm', 'height (cm)'
        ],
        'leaf_count': ['leaves', 'leaf count', 'number of leaves', 'leaf_number'],
        'flowering_percentage': [
            'flowering', 'flowering %', 'flowering percent',
            'percent flowering', 'bloom'
        ],

        # Financial
        'amount': ['amount', 'cost', 'price', 'value', 'total'],
        'transaction_type': ['type', 'transaction type', 'category'],
        'description': ['description', 'desc', 'notes', 'details'],
        'quantity': ['quantity', 'qty', 'amount', 'count'],
        'unit': ['unit', 'uom', 'unit of measure'],
        'price_per_unit': ['price', 'unit price', 'price per unit', 'rate'],

        # Common
        'notes': ['notes', 'comments', 'remarks', 'description'],
        'soil_type': ['soil', 'soil type', 'soil_class'],
        'crop_type': ['crop', 'crop type', 'crop_name', 'plant'],
    }

    @staticmethod
    def normalize_column_name(name: str) -> str:
        """
        Normalize column name for comparison.

        Args:
            name: Original column name

        Returns:
            Normalized column name (lowercase, spaces to underscores)
        """
        # Convert to lowercase
        normalized = name.lower()
        # Remove special characters except spaces and underscores
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # Replace spaces with underscores
        normalized = re.sub(r'\s+', '_', normalized)
        # Remove multiple underscores
        normalized = re.sub(r'_+', '_', normalized)
        # Strip leading/trailing underscores
        normalized = normalized.strip('_')
        return normalized

    @staticmethod
    def calculate_similarity(source: str, target: str) -> float:
        """
        Calculate similarity score between two strings.

        Args:
            source: Source column name
            target: Target column name

        Returns:
            Similarity score (0-100)
        """
        # Normalize both strings
        source_norm = ColumnMapper.normalize_column_name(source)
        target_norm = ColumnMapper.normalize_column_name(target)

        # Exact match
        if source_norm == target_norm:
            return 100.0

        # Use SequenceMatcher for fuzzy matching
        similarity = SequenceMatcher(None, source_norm, target_norm).ratio()

        return round(similarity * 100, 2)

    @staticmethod
    def find_best_match(
        source_column: str,
        target_columns: List[str],
        min_confidence: float = 60.0
    ) -> Tuple[Optional[str], float, List[Dict[str, any]]]:
        """
        Find best matching target column for a source column.

        Args:
            source_column: Source column name from file
            target_columns: List of available target column names
            min_confidence: Minimum confidence threshold

        Returns:
            Tuple of (best_match, confidence, alternatives)
        """
        scores = []

        for target_col in target_columns:
            # Check direct similarity
            direct_score = ColumnMapper.calculate_similarity(source_column, target_col)

            # Check alias matches
            alias_score = 0.0
            if target_col in ColumnMapper.COLUMN_ALIASES:
                aliases = ColumnMapper.COLUMN_ALIASES[target_col]
                alias_scores = [
                    ColumnMapper.calculate_similarity(source_column, alias)
                    for alias in aliases
                ]
                alias_score = max(alias_scores) if alias_scores else 0.0

            # Use the better score
            best_score = max(direct_score, alias_score)

            if best_score >= min_confidence:
                scores.append({
                    'target_column': target_col,
                    'confidence': best_score
                })

        # Sort by confidence (descending)
        scores.sort(key=lambda x: x['confidence'], reverse=True)

        if scores:
            best_match = scores[0]['target_column']
            confidence = scores[0]['confidence']
            alternatives = scores[1:4]  # Top 3 alternatives
            return best_match, confidence, alternatives
        else:
            return None, 0.0, []

    @staticmethod
    def auto_map_columns(
        source_columns: List[str],
        data_type: str,
        min_confidence: float = 60.0
    ) -> Dict[str, any]:
        """
        Automatically map source columns to target schema.

        Args:
            source_columns: List of column names from uploaded file
            data_type: Type of data being imported
            min_confidence: Minimum confidence threshold for auto-mapping

        Returns:
            Dictionary with mapping results
        """
        if data_type not in ColumnMapper.COLUMN_SCHEMAS:
            raise ValueError(f"Unknown data type: {data_type}")

        schema = ColumnMapper.COLUMN_SCHEMAS[data_type]
        all_target_columns = schema['required'] + schema['optional']

        # Map each source column
        mappings = []
        mapped_targets = set()

        for source_col in source_columns:
            best_match, confidence, alternatives = ColumnMapper.find_best_match(
                source_col,
                all_target_columns,
                min_confidence
            )

            # Avoid mapping multiple source columns to same target
            if best_match and best_match in mapped_targets:
                # Use second best if available
                if alternatives:
                    for alt in alternatives:
                        if alt['target_column'] not in mapped_targets:
                            best_match = alt['target_column']
                            confidence = alt['confidence']
                            break

            if best_match:
                mapped_targets.add(best_match)

            mappings.append({
                'source_column': source_col,
                'target_column': best_match,
                'confidence': confidence,
                'alternatives': alternatives
            })

        # Identify unmapped columns
        unmapped_sources = [
            m['source_column'] for m in mappings if m['target_column'] is None
        ]

        # Identify missing required columns
        required_missing = [
            col for col in schema['required'] if col not in mapped_targets
        ]

        result = {
            'mappings': mappings,
            'unmapped_columns': unmapped_sources,
            'required_columns_missing': required_missing,
            'mapping_quality': ColumnMapper._calculate_mapping_quality(mappings, schema)
        }

        logger.info(
            f"Auto-mapping complete: {len(mapped_targets)}/{len(all_target_columns)} "
            f"columns mapped, {len(required_missing)} required columns missing"
        )

        return result

    @staticmethod
    def _calculate_mapping_quality(
        mappings: List[Dict],
        schema: Dict
    ) -> Dict[str, any]:
        """Calculate overall mapping quality metrics."""
        total_mappings = len([m for m in mappings if m['target_column'] is not None])
        required_count = len(schema['required'])
        required_mapped = len([
            m for m in mappings
            if m['target_column'] in schema['required']
        ])

        avg_confidence = sum(m['confidence'] for m in mappings) / len(mappings) if mappings else 0

        return {
            'total_mapped': total_mappings,
            'required_mapped': required_mapped,
            'required_total': required_count,
            'average_confidence': round(avg_confidence, 2),
            'is_complete': required_mapped == required_count
        }

    @staticmethod
    def apply_manual_mapping(
        auto_mapping: Dict[str, any],
        manual_overrides: Dict[str, str]
    ) -> Dict[str, any]:
        """
        Apply manual column mapping overrides.

        Args:
            auto_mapping: Result from auto_map_columns
            manual_overrides: Dict mapping source columns to target columns

        Returns:
            Updated mapping result
        """
        mappings = auto_mapping['mappings'].copy()

        for i, mapping in enumerate(mappings):
            source = mapping['source_column']
            if source in manual_overrides:
                mappings[i]['target_column'] = manual_overrides[source]
                mappings[i]['confidence'] = 100.0  # Manual mapping is 100% confident
                mappings[i]['manual_override'] = True

        # Recalculate derived fields
        mapped_targets = {m['target_column'] for m in mappings if m['target_column']}
        unmapped_sources = [
            m['source_column'] for m in mappings if m['target_column'] is None
        ]

        data_type = auto_mapping.get('data_type', 'farms_plots')
        schema = ColumnMapper.COLUMN_SCHEMAS.get(data_type, {})
        required_missing = [
            col for col in schema.get('required', [])
            if col not in mapped_targets
        ]

        return {
            'mappings': mappings,
            'unmapped_columns': unmapped_sources,
            'required_columns_missing': required_missing,
            'mapping_quality': ColumnMapper._calculate_mapping_quality(mappings, schema)
        }

    @staticmethod
    def get_mapping_dict(mapping_result: Dict[str, any]) -> Dict[str, str]:
        """
        Extract simple source->target mapping dictionary.

        Args:
            mapping_result: Result from auto_map_columns or apply_manual_mapping

        Returns:
            Dictionary mapping source columns to target columns
        """
        return {
            m['source_column']: m['target_column']
            for m in mapping_result['mappings']
            if m['target_column'] is not None
        }
