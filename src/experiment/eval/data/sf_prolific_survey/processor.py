import os
import json
import pandas as pd
from pathlib import Path
import re

class SurveyDataProcessor:
    def __init__(self, input_dir=None, output_dir=None):
        """
        Initialize the processor with directories for input and output.
        
        Args:
            input_dir: Directory containing raw CSV files
            output_dir: Directory where processed files will be saved
        """
        # Get the base directory (sf_prolific_survey)
        base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
        # Set input and output directories
        self.input_dir = Path(input_dir) if input_dir else base_dir / "raw"
        self.output_dir = Path(output_dir) if output_dir else base_dir / "processed"
            
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
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
                
                # Initialize reactions for this participant
                reactions[pid] = {'opinions': {}, 'reasons': {}}
                
                # Find all scenario columns
                scenario_pattern = r'^Scenario \d+\.\d+'
                reason_pattern = r'^Scenario \d+\.\d+: Select the reasons'
                
                # Extract opinions (numeric ratings)
                opinion_columns = [col for col in df.columns if re.match(scenario_pattern, col) and not re.match(reason_pattern, col)]
                
                # Extract reasons
                reason_columns = [col for col in df.columns if re.match(reason_pattern, col)]
                
                # Process opinions
                for col in opinion_columns:
                    if col in participant_data.columns:
                        scenario_id = col.replace('Scenario ', '').strip()
                        reactions[pid]['opinions'][scenario_id] = int(participant_data[col].iloc[0])
                
                # Process reasons
                for col in reason_columns:
                    if col in participant_data.columns:
                        scenario_id = col.replace('Scenario ', '').replace(': Select the reasons', '').strip()
                        reasons_text = participant_data[col].iloc[0]
                        
                        # Split reasons if they're in a comma-separated list
                        if isinstance(reasons_text, str):
                            reasons_list = [reason.strip() for reason in reasons_text.split(',')]
                            reactions[pid]['reasons'][scenario_id] = reasons_list
                        else:
                            reactions[pid]['reasons'][scenario_id] = reasons_text
            
            # Save extracted data to JSON files
            base_name = csv_file.stem
            
            # Save demographics
            demographics_file = self.output_dir / f"{base_name}_demographics.json"
            with open(demographics_file, 'w') as f:
                json.dump(demographics, f, indent=2)
                
            # Save reactions
            reactions_file = self.output_dir / f"{base_name}_reactions.json"
            with open(reactions_file, 'w') as f:
                json.dump(reactions, f, indent=2)
                
            print(f"Successfully processed {csv_file.name}.")
            print(f"Demographic data saved to {demographics_file}")
            print(f"Reaction data saved to {reactions_file}")
            
        except Exception as e:
            print(f"Error processing {csv_file.name}: {str(e)}")

if __name__ == "__main__":
    processor = SurveyDataProcessor()
    processor.process_csv_files() 