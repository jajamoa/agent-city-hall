import React, { useState } from 'react';

const SimulationHandler = ({ proposal, onSimulationResults }) => {
  const [isSimulating, setIsSimulating] = useState(false);

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      // Placeholder: 3s delay simulation
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Mock response data
      const mockResult = {
        summary: {
          support: 60,
          oppose: 30,
          neutral: 10
        },
        comments: [
          {
            id: 1,
            agent: {
              age: 35,
              occupation: "Software Engineer",
              neighborhood: "Mission"
            },
            sentiment: "support",
            comment: "This proposal will help address housing needs.",
            location: {
              longitude: -122.4194,
              latitude: 37.7749
            }
          },
          // Add more mock data as needed
        ]
      };

      onSimulationResults?.(mockResult);
    } catch (error) {
      console.error('Error during simulation:', error);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <button
      className={`dark-button simulate-button ${isSimulating ? 'loading' : ''}`}
      onClick={handleSimulate}
      disabled={isSimulating}
    >
      {isSimulating ? (
        <>
          <div className="spinner">
            <div className="spinner-inner"></div>
          </div>
          Loading
        </>
      ) : (
        'Simulate'
      )}
    </button>
  );
};

export default SimulationHandler; 