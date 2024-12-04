import React, { useState, useEffect } from 'react';
import ScatterPlot from './ScatterPlot.jsx';
import FilterPanel from './FilterPanel';
import DetailPanel from './DetailPanel';
import axios from 'axios';

const CommentVisualizer = () => {
  const [data, setData] = useState(null);
  const [filters, setFilters] = useState({
    site: 'all',
    opinion: 'all',
  });
  const [selectedPoint, setSelectedPoint] = useState(null);

  useEffect(() => {
    axios.get('/data/visualization_data.json')
      .then(response => setData(response.data))
      .catch(error => console.error('Error loading data:', error));
  }, []);

  const filteredData = data?.points.filter(point =>
    (filters.site === 'all' || point.site === filters.site) &&
    (filters.opinion === 'all' || point.opinion === filters.opinion)
  );

  return (
    <div className="visualizer-container">
      <FilterPanel 
        filters={filters}
        setFilters={setFilters}
        metadata={data?.metadata}
      />
      <div className="main-content">
        <ScatterPlot 
          data={filteredData}
          onPointSelect={setSelectedPoint}
        />
      </div>
      <DetailPanel point={selectedPoint} />
    </div>
  );
};

export default CommentVisualizer;