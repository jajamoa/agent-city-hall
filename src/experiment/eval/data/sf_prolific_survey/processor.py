import os
import json
import pandas as pd
from pathlib import Path
import re

class SurveyDataProcessor:
    def __init__(self, input_dir=None, output_dir=None, mapping_file=None):
        """
        Initialize the processor with directories for input and output.
        
        Args:
            input_dir: Directory containing raw CSV files
            output_dir: Directory where processed files will be saved
            mapping_file: Path to the reason mapping JSON file
        """
        # Get the base directory (sf_prolific_survey)
        base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
        # Set input and output directories
        self.input_dir = Path(input_dir) if input_dir else base_dir / "raw"
        self.output_dir = Path(output_dir) if output_dir else base_dir / "processed"
            
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load reason mapping
        self.mapping_file = Path(mapping_file) if mapping_file else base_dir / "reason_mapping.json"
        self.load_reason_mapping()
    
    def load_reason_mapping(self):
        """Load the reason mapping from JSON file."""
        try:
            if self.mapping_file.exists():
                with open(self.mapping_file, 'r') as f:
                    mapping_data = json.load(f)
                self.reason_mapping = mapping_data.get("mapping", {})
                self.reverse_mapping = mapping_data.get("reverse_mapping", {})
                print(f"Loaded reason mapping from {self.mapping_file}")
            else:
                print(f"Warning: Reason mapping file {self.mapping_file} not found")
                self.reason_mapping = {}
                self.reverse_mapping = {}
        except Exception as e:
            print(f"Error loading reason mapping: {str(e)}")
            self.reason_mapping = {}
            self.reverse_mapping = {}
    
    def process_csv_files(self):
        """Process all CSV files in the input directory."""
        csv_files = list(self.input_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"No CSV files found in {self.input_dir}")
            return
            
        # Process each CSV file
        for csv_file in csv_files:
            print(f"Processing {csv_file.name}...")
            self._process_single_file(csv_file)
    
    def _process_single_file(self, csv_file):
        """
        Process a single CSV file to extract demographic and reaction information.
        
        Args:
            csv_file: Path to the CSV file
        """
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Extract participant IDs from "Prolific ID" column
            if 'Prolific ID' in df.columns:
                participant_ids = df['Prolific ID'].unique()
            else:
                print(f"Warning: 'Prolific ID' column not found in {csv_file.name}")
                participant_ids = []
            
            demographics = {}
            reactions = {}
            reactions_mapped = {}
            
            # Define demographic columns
            demographic_columns = [
                'What is your age?', 
                'Have you moved in the past year?', 
                'If you rent, what is your approximate monthly rent as a percentage of your income?',
                'What best describes your housing status?',
                'What is your primary mode of transportation? (Please select all that apply)',
                'What is your annual household income?',
                'Which of the following best describes your occupation?',
                'Which of the following best describes your household and family situation?',
                'What is your ZIP code?',
                "What's your address?"
            ]
            
            # List of predefined reason categories
            reason_categories = list(self.reason_mapping.keys()) if self.reason_mapping else [
                "Housing supply and availability",
                "Affordability for low- and middle-income residents",
                "Neighborhood character and visual compatibility",
                "Traffic and parking availability",
                "Walkability and access to amenities",
                "Noise, congestion, or infrastructure strain",
                "Fairness and distribution of development across neighborhoods",
                "Economic vitality for local businesses",
                "Building height or scale relative to surroundings",
                "Personal property values or homeownership concerns",
                "Integration of new residents into community life",
                "School quality or capacity in the area"
            ]
            
            # Process each participant
            for pid in participant_ids:
                participant_data = df[df['Prolific ID'] == pid]
                
                # Extract demographic information
                demographics[pid] = {
                    col: participant_data[col].iloc[0] 
                    for col in demographic_columns 
                    if col in participant_data.columns
                }
                
                # Add housing experience as demographic information
                if 'In the past five years, briefly describe your housing experience in San Francisco, including any moves, rental situations, and changes in your housing status. What were the reasons for these changes?' in participant_data.columns:
                    demographics[pid]['housing_experience'] = participant_data['In the past five years, briefly describe your housing experience in San Francisco, including any moves, rental situations, and changes in your housing status. What were the reasons for these changes?'].iloc[0]
                
                # Initialize reactions for this participant with simplified structure
                reactions[pid] = {
                    'opinions': {},
                    'reasons': {}
                }
                
                # Initialize mapped reactions
                reactions_mapped[pid] = {
                    'opinions': {},
                    'reasons': {}
                }
                
                # Find all scenario columns
                scenario_pattern = r'^Scenario (\d+\.\d+)'
                reason_pattern = r'^Scenario (\d+\.\d+): Select the reasons'
                
                # Extract opinions (numeric ratings)
                for col in df.columns:
                    # Match scenario columns for opinions
                    opinion_match = re.match(scenario_pattern, col)
                    if opinion_match and not re.match(reason_pattern, col):
                        scenario_id = opinion_match.group(1)  # Extract just the number (e.g., "1.1")
                        if col in participant_data.columns:
                            value = int(participant_data[col].iloc[0])
                            reactions[pid]['opinions'][scenario_id] = value
                            reactions_mapped[pid]['opinions'][scenario_id] = value
                
                # Extract reasons
                for col in df.columns:
                    # Match scenario columns for reasons
                    reason_match = re.match(reason_pattern, col)
                    if reason_match:
                        scenario_id = reason_match.group(1)  # Extract just the number (e.g., "1.1")
                        if col in participant_data.columns:
                            reasons_text = participant_data[col].iloc[0]
                            
                            # Parse reasons into a list
                            if isinstance(reasons_text, str):
                                # Instead of just splitting by comma, extract each complete reason phrase
                                reasons_list = []
                                for category in reason_categories:
                                    if category in reasons_text:
                                        reasons_list.append(category)
                                
                                # If we didn't find any matches using the predefined list,
                                # fall back to simple splitting as a last resort
                                if not reasons_list and ',' in reasons_text:
                                    reasons_list = [reason.strip() for reason in reasons_text.split(',')]
                                
                                # Apply mapping to reasons
                                mapped_reasons = []
                                for reason in reasons_list:
                                    if reason in self.reason_mapping:
                                        mapped_reasons.append(self.reason_mapping[reason])
                                    else:
                                        # If not in mapping, keep original
                                        mapped_reasons.append(reason)
                                
                                reactions[pid]['reasons'][scenario_id] = reasons_list
                                reactions_mapped[pid]['reasons'][scenario_id] = mapped_reasons
                            else:
                                reactions[pid]['reasons'][scenario_id] = reasons_text
                                reactions_mapped[pid]['reasons'][scenario_id] = reasons_text
            
            # Save extracted data to JSON files
            base_name = csv_file.stem
            
            # Save demographics
            demographics_file = self.output_dir / f"{base_name}_demographics.json"
            with open(demographics_file, 'w') as f:
                json.dump(demographics, f, indent=2)
            
            # Save reactions with text labels
            reactions_file = self.output_dir / f"{base_name}_reactions.json"
            with open(reactions_file, 'w') as f:
                json.dump(reactions, f, indent=2)
                
            # Save reactions with mapped codes
            reactions_mapped_file = self.output_dir / f"{base_name}_reactions_mapped.json"
            with open(reactions_mapped_file, 'w') as f:
                json.dump(reactions_mapped, f, indent=2)
                
            print(f"Successfully processed {csv_file.name}.")
            print(f"Demographic data saved to {demographics_file}")
            print(f"Reaction data saved to {reactions_file}")
            print(f"Mapped reaction data saved to {reactions_mapped_file}")
            
        except Exception as e:
            print(f"Error processing {csv_file.name}: {str(e)}")

if __name__ == "__main__":
    processor = SurveyDataProcessor()
    processor.process_csv_files() 