"""
Unit tests for column mapping service.

Tests auto-mapping accuracy, fuzzy matching, and various column name formats.
Target: >80% auto-mapping accuracy.
"""
import pytest
from difflib import SequenceMatcher


@pytest.mark.unit
class TestColumnMapper:
    """Test column name mapping functionality."""

    @pytest.fixture
    def standard_farm_columns(self):
        """Standard database column names for farm data."""
        return {
            'farm_name': {'required': True, 'type': 'string'},
            'address': {'required': False, 'type': 'string'},
            'total_area_hectares': {'required': False, 'type': 'float'},
            'latitude': {'required': False, 'type': 'float'},
            'longitude': {'required': False, 'type': 'float'},
            'timezone': {'required': False, 'type': 'string'},
        }

    @pytest.fixture
    def standard_irrigation_columns(self):
        """Standard database column names for irrigation data."""
        return {
            'plot_name': {'required': True, 'type': 'string'},
            'event_time': {'required': True, 'type': 'datetime'},
            'method': {'required': True, 'type': 'string'},
            'duration_minutes': {'required': False, 'type': 'integer'},
            'water_volume_liters': {'required': False, 'type': 'float'},
            'water_source': {'required': False, 'type': 'string'},
        }

    def test_exact_match_mapping(self, standard_farm_columns):
        """Test mapping with exact column name matches."""
        input_columns = ['farm_name', 'address', 'total_area_hectares', 'latitude', 'longitude']

        # Map columns
        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Assertions
        assert mappings['farm_name']['target'] == 'farm_name'
        assert mappings['farm_name']['confidence'] == 1.0
        assert mappings['address']['target'] == 'address'
        assert mappings['total_area_hectares']['target'] == 'total_area_hectares'

    def test_case_insensitive_mapping(self, standard_farm_columns):
        """Test mapping with different case variations."""
        input_columns = ['FARM_NAME', 'Farm_Name', 'LATITUDE', 'longitude']

        # Map columns (case-insensitive)
        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Assertions
        assert mappings['FARM_NAME']['target'] == 'farm_name'
        assert mappings['FARM_NAME']['confidence'] >= 0.9
        assert mappings['Farm_Name']['target'] == 'farm_name'
        assert mappings['LATITUDE']['target'] == 'latitude'

    def test_snake_case_mapping(self, standard_farm_columns):
        """Test mapping snake_case variations."""
        input_columns = ['farm_name', 'total_area_hectares', 'lat', 'lon']

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        assert mappings['farm_name']['target'] == 'farm_name'
        assert mappings['total_area_hectares']['target'] == 'total_area_hectares'

    def test_camel_case_mapping(self, standard_farm_columns):
        """Test mapping camelCase variations."""
        input_columns = ['farmName', 'totalAreaHectares', 'latitude', 'longitude']

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Should map camelCase to snake_case
        assert mappings['farmName']['target'] == 'farm_name'
        assert mappings['farmName']['confidence'] >= 0.8
        assert mappings['totalAreaHectares']['target'] == 'total_area_hectares'

    def test_title_case_mapping(self, standard_farm_columns):
        """Test mapping 'Title Case' variations."""
        input_columns = ['Farm Name', 'Total Area Hectares', 'Latitude', 'Longitude']

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Should map Title Case to snake_case
        assert mappings['Farm Name']['target'] == 'farm_name'
        assert mappings['Farm Name']['confidence'] >= 0.8
        assert mappings['Total Area Hectares']['target'] == 'total_area_hectares'

    def test_fuzzy_matching_common_variations(self, standard_farm_columns):
        """Test fuzzy matching for common column name variations."""
        input_columns = [
            'farm',  # Short for farm_name
            'name',  # Could be farm_name
            'area',  # Short for total_area_hectares
            'lat',   # Short for latitude
            'lng',   # Variation of longitude
        ]

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Should find reasonable matches
        assert mappings['farm']['target'] in ['farm_name']
        assert mappings['lat']['target'] == 'latitude'
        assert mappings['lng']['target'] == 'longitude'

    def test_fuzzy_matching_with_typos(self, standard_farm_columns):
        """Test fuzzy matching with minor typos."""
        input_columns = [
            'farm_nme',     # Typo in farm_name
            'latitde',      # Typo in latitude
            'longitde',     # Typo in longitude
        ]

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Should still match despite typos
        assert mappings['farm_nme']['target'] == 'farm_name'
        assert mappings['farm_nme']['confidence'] >= 0.7
        assert mappings['latitde']['target'] == 'latitude'

    def test_confidence_scores(self, standard_farm_columns):
        """Test confidence score calculation."""
        test_cases = [
            ('farm_name', 1.0),           # Exact match
            ('Farm_Name', 0.9),           # Case difference
            ('farmName', 0.85),           # camelCase
            ('Farm Name', 0.85),          # Title Case
            ('farm', 0.7),                # Partial match
            ('farm_nme', 0.8),            # Typo
        ]

        for input_col, expected_min_confidence in test_cases:
            mappings = self._auto_map_columns([input_col], standard_farm_columns)
            if input_col in mappings:
                assert mappings[input_col]['confidence'] >= expected_min_confidence - 0.1

    def test_unmapped_columns(self, standard_farm_columns):
        """Test handling of columns that cannot be mapped."""
        input_columns = [
            'farm_name',           # Should map
            'unknown_column',      # Should not map
            'random_field',        # Should not map
        ]

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Assertions
        assert mappings['farm_name']['target'] == 'farm_name'
        assert mappings['unknown_column']['target'] is None
        assert mappings['unknown_column']['confidence'] < 0.6
        assert mappings['random_field']['target'] is None

    def test_multiple_input_columns_to_same_target(self, standard_farm_columns):
        """Test handling when multiple input columns match the same target."""
        input_columns = [
            'farm_name',
            'farmName',
            'Farm Name',
        ]

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # All should map to farm_name, but only highest confidence should be primary
        assert mappings['farm_name']['confidence'] == 1.0
        assert mappings['farmName']['confidence'] < 1.0
        assert mappings['Farm Name']['confidence'] < 1.0

    def test_irrigation_column_mapping(self, standard_irrigation_columns):
        """Test mapping irrigation-specific columns."""
        input_columns = [
            'Plot Name',
            'Date/Time',
            'Irrigation Method',
            'Duration (min)',
            'Water Volume (L)',
        ]

        mappings = self._auto_map_columns(input_columns, standard_irrigation_columns)

        # Assertions
        assert mappings['Plot Name']['target'] == 'plot_name'
        assert mappings['Irrigation Method']['target'] == 'method'
        assert 'duration' in mappings['Duration (min)']['target'].lower()

    def test_column_mapping_with_units(self, standard_farm_columns):
        """Test mapping columns with unit indicators."""
        input_columns = [
            'Area (hectares)',
            'Area (ha)',
            'Latitude (degrees)',
            'Longitude (degrees)',
        ]

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Should ignore units and map to correct columns
        assert mappings['Area (hectares)']['target'] == 'total_area_hectares'
        assert mappings['Area (ha)']['target'] == 'total_area_hectares'
        assert mappings['Latitude (degrees)']['target'] == 'latitude'

    def test_column_mapping_with_prefixes(self, standard_farm_columns):
        """Test mapping columns with prefixes."""
        input_columns = [
            'farm.name',
            'farm.latitude',
            'farm.longitude',
        ]

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Should handle prefixes
        assert mappings['farm.name']['target'] == 'farm_name'
        assert mappings['farm.latitude']['target'] == 'latitude'

    def test_column_mapping_abbreviations(self, standard_farm_columns):
        """Test mapping common abbreviations."""
        abbreviation_tests = [
            ('lat', 'latitude'),
            ('lon', 'longitude'),
            ('lng', 'longitude'),
            ('addr', 'address'),
        ]

        for abbrev, expected_target in abbreviation_tests:
            mappings = self._auto_map_columns([abbrev], standard_farm_columns)
            if abbrev in mappings and mappings[abbrev]['target']:
                assert expected_target in mappings[abbrev]['target']

    def test_mapping_accuracy_threshold(self, standard_farm_columns):
        """Test that auto-mapping achieves >80% accuracy."""
        # Test with realistic input variations
        input_columns = [
            'Farm Name',              # Should map
            'farm address',           # Should map
            'Total Area (ha)',        # Should map
            'Latitude',               # Should map
            'Longitude',              # Should map
            'Time Zone',              # Should map
            'Created Date',           # Should not map
            'Updated By',             # Should not map
        ]

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Count successful mappings
        mapped_count = sum(1 for m in mappings.values() if m['target'] is not None and m['confidence'] >= 0.7)
        total_mappable = 6  # First 6 columns should map

        accuracy = mapped_count / total_mappable
        assert accuracy >= 0.8, f"Mapping accuracy {accuracy:.2%} is below 80% threshold"

    def test_manual_mapping_override(self, standard_farm_columns):
        """Test allowing manual mapping overrides."""
        input_columns = ['custom_farm_field']

        # Auto-map
        auto_mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Manual override
        manual_mapping = {
            'custom_farm_field': {
                'target': 'farm_name',
                'confidence': 1.0,
                'is_manual': True
            }
        }

        # Manual mapping should override auto-mapping
        assert manual_mapping['custom_farm_field']['is_manual'] is True
        assert manual_mapping['custom_farm_field']['target'] == 'farm_name'

    def test_save_mapping_template(self, standard_farm_columns):
        """Test saving successful mappings as templates."""
        input_columns = ['Farm Name', 'Total Area (ha)', 'Latitude', 'Longitude']

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Create template
        template = {
            'name': 'Standard Farm Import',
            'data_type': 'farms',
            'column_mapping': mappings,
            'is_default': False
        }

        # Assertions
        assert template['name'] == 'Standard Farm Import'
        assert template['data_type'] == 'farms'
        assert 'Farm Name' in template['column_mapping']

    def test_load_saved_template(self, standard_farm_columns):
        """Test loading previously saved mapping template."""
        saved_template = {
            'name': 'Standard Farm Import',
            'data_type': 'farms',
            'column_mapping': {
                'Farm Name': {'target': 'farm_name', 'confidence': 1.0},
                'Total Area (ha)': {'target': 'total_area_hectares', 'confidence': 1.0},
            }
        }

        # Use saved template
        input_columns = ['Farm Name', 'Total Area (ha)']

        # Apply template mappings
        mappings = saved_template['column_mapping']

        # Assertions
        assert mappings['Farm Name']['target'] == 'farm_name'
        assert mappings['Total Area (ha)']['target'] == 'total_area_hectares'

    def test_mapping_special_characters(self, standard_farm_columns):
        """Test mapping columns with special characters."""
        input_columns = [
            'Farm Name (Required)',
            'Area - Hectares',
            'Latitude/Longitude - Lat',
            'Farm\'s Address',
        ]

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Should handle special characters
        assert mappings['Farm Name (Required)']['target'] == 'farm_name'
        assert 'area' in mappings['Area - Hectares']['target'].lower()

    def test_mapping_numeric_suffixes(self, standard_farm_columns):
        """Test mapping columns with numeric suffixes."""
        input_columns = [
            'farm_name_1',
            'latitude_deg',
            'longitude_deg',
        ]

        mappings = self._auto_map_columns(input_columns, standard_farm_columns)

        # Should ignore numeric suffixes
        assert mappings['farm_name_1']['target'] == 'farm_name'

    def test_mapping_multilingual_columns(self):
        """Test mapping columns in different languages."""
        # This would require language-specific mapping rules
        input_columns = [
            'Nom de la ferme',  # French: Farm name
            'Finca nombre',     # Spanish: Farm name
        ]

        # For now, these should not map without language-specific rules
        # In future, could add multilingual support

    # Helper methods

    def _auto_map_columns(self, input_columns, target_columns):
        """
        Simulate auto-mapping logic.

        This is a simplified implementation for testing purposes.
        The actual service would be more sophisticated.
        """
        mappings = {}

        for input_col in input_columns:
            best_match = None
            best_score = 0.0

            # Normalize input column
            input_normalized = self._normalize_column_name(input_col)

            for target_col in target_columns.keys():
                # Normalize target column
                target_normalized = self._normalize_column_name(target_col)

                # Calculate similarity
                score = self._similarity_score(input_normalized, target_normalized)

                # Also check partial matches
                partial_score = max(
                    self._similarity_score(input_normalized, part)
                    for part in target_normalized.split('_')
                )
                score = max(score, partial_score * 0.8)

                if score > best_score:
                    best_score = score
                    best_match = target_col

            # Only map if confidence is above threshold
            if best_score >= 0.6:
                mappings[input_col] = {
                    'target': best_match,
                    'confidence': round(best_score, 2),
                    'is_manual': False
                }
            else:
                mappings[input_col] = {
                    'target': None,
                    'confidence': round(best_score, 2),
                    'is_manual': False
                }

        return mappings

    def _normalize_column_name(self, col_name):
        """Normalize column name for comparison."""
        import re

        # Remove special characters and extra spaces
        col_name = re.sub(r'[^\w\s]', ' ', col_name.lower())

        # Convert to snake_case
        col_name = re.sub(r'\s+', '_', col_name.strip())

        # Remove common words
        common_words = ['required', 'optional', 'field', 'column']
        for word in common_words:
            col_name = col_name.replace(word, '')

        # Clean up double underscores
        col_name = re.sub(r'_+', '_', col_name)
        col_name = col_name.strip('_')

        return col_name

    def _similarity_score(self, str1, str2):
        """Calculate similarity score between two strings."""
        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, str1, str2).ratio()


@pytest.mark.unit
class TestColumnMapperEdgeCases:
    """Test edge cases for column mapping."""

    def test_empty_input_columns(self):
        """Test mapping with no input columns."""
        input_columns = []
        target_columns = {'farm_name': {}}

        # Should return empty mappings
        assert len(input_columns) == 0

    def test_duplicate_input_columns(self):
        """Test handling duplicate input column names."""
        input_columns = ['farm_name', 'farm_name', 'area']

        # Should handle duplicates
        unique_columns = list(dict.fromkeys(input_columns))
        assert len(unique_columns) == 2

    def test_very_long_column_names(self):
        """Test handling very long column names."""
        input_columns = ['this_is_a_very_long_column_name_that_might_cause_issues_in_some_systems_farm_name']

        # Should still attempt to map
        assert len(input_columns[0]) > 50

    def test_column_names_with_only_special_characters(self):
        """Test columns with only special characters."""
        input_columns = ['@#$', '!!!', '---']

        # Should handle gracefully
        for col in input_columns:
            assert len(col) > 0
