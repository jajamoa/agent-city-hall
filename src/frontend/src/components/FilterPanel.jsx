import React from 'react';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

const FilterPanel = ({ filters, setFilters, metadata }) => {
  if (!metadata) return null;

  return (
    <div className="filter-panel">
      <h3>Filters</h3>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Site</InputLabel>
        <Select
          value={filters.site}
          label="Site"
          onChange={(e) => setFilters({ ...filters, site: e.target.value })}
        >
          <MenuItem value="all">All Sites</MenuItem>
          {metadata.sites.map(site => (
            <MenuItem key={site} value={site}>{site}</MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth>
        <InputLabel>Opinion</InputLabel>
        <Select
          value={filters.opinion}
          label="Opinion"
          onChange={(e) => setFilters({ ...filters, opinion: e.target.value })}
        >
          <MenuItem value="all">All Opinions</MenuItem>
          {metadata.opinions.map(opinion => (
            <MenuItem key={opinion} value={opinion}>{opinion}</MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  );
};

export default FilterPanel;