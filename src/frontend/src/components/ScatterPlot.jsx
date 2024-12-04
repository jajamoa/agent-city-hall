import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

const ScatterPlot = ({ data, onPointSelect }) => {
  const svgRef = useRef();
  const [transform, setTransform] = useState(d3.zoomIdentity);
  const zoomRef = useRef();
  const gRef = useRef();

  useEffect(() => {
    if (!data) return;

    const width = 800;
    const height = 600;
    const margin = { top: 20, right: 20, bottom: 30, left: 40 };

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    svg.selectAll('*').remove();

    const xExtent = d3.extent(data, d => d.x);
    const yExtent = d3.extent(data, d => d.y);
    
    const xPadding = (xExtent[1] - xExtent[0]) * 0.05;
    const yPadding = (yExtent[1] - yExtent[0]) * 0.05;

    const xScale = d3.scaleLinear()
      .domain([xExtent[0] - xPadding, xExtent[1] + xPadding])
      .range([margin.left, width - margin.right]);

    const yScale = d3.scaleLinear()
      .domain([yExtent[0] - yPadding, yExtent[1] + yPadding])
      .range([height - margin.bottom, margin.top]);

    // Store zoom behavior in ref
    if (!zoomRef.current) {
      zoomRef.current = d3.zoom()
        .scaleExtent([0.5, 5])
        .on('zoom', (event) => {
          gRef.current.attr('transform', event.transform);
          setTransform(event.transform);
        });
    }

    svg.call(zoomRef.current);

    // Apply stored transform
    const g = svg.append('g')
      .attr('transform', transform);
    
    gRef.current = g;

    const colorScale = d3.scaleOrdinal()
      .domain(['Support', 'Oppose', 'Neutral'])
      .range(['#2ecc71', '#e74c3c', '#95a5a6']);

    g.selectAll('circle')
      .data(data)
      .join('circle')
      .attr('cx', d => xScale(d.x))
      .attr('cy', d => yScale(d.y))
      .attr('r', 6)
      .attr('fill', d => colorScale(d.opinion))
      .attr('opacity', 0.7)
      .on('mouseover', (event, d) => {
        d3.select(event.currentTarget)
          .attr('r', 9)
          .attr('opacity', 1)
          .raise();
      })
      .on('mouseout', (event, d) => {
        d3.select(event.currentTarget)
          .attr('r', 6)
          .attr('opacity', 0.7);
      })
      .on('click', (event, d) => {
        onPointSelect(d);
      });

    const tooltip = d3.select('body').append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background-color', 'rgba(0, 0, 0, 0.8)')
      .style('color', '#fff')
      .style('padding', '8px')
      .style('border-radius', '4px')
      .style('font-size', '12px');

    g.selectAll('circle')
      .on('mouseover', (event, d) => {
        tooltip
          .style('visibility', 'visible')
          .html(`Site: ${d.site}<br/>Opinion: ${d.opinion}<br/>Date: ${d.date}`);
      })
      .on('mousemove', (event) => {
        tooltip
          .style('top', (event.pageY - 10) + 'px')
          .style('left', (event.pageX + 10) + 'px');
      })
      .on('mouseout', () => {
        tooltip.style('visibility', 'hidden');
      });

    const resetButton = svg.append('g')
      .attr('class', 'reset-button')
      .style('cursor', 'pointer')
      .on('click', () => {
        svg.transition()
          .duration(750)
          .call(zoomRef.current.transform, d3.zoomIdentity);
      });

    resetButton.append('rect')
      .attr('x', 10)
      .attr('y', 10)
      .attr('width', 80)
      .attr('height', 30)
      .attr('fill', 'rgba(255, 255, 255, 0.1)')
      .attr('rx', 4);

    resetButton.append('text')
      .attr('x', 20)
      .attr('y', 30)
      .attr('fill', '#d1d5db')
      .style('font-size', '12px')
      .text('Reset View');

    return () => {
      tooltip.remove();
    };
  }, [data, transform]);

  return <svg ref={svgRef}></svg>;
};

export default ScatterPlot;