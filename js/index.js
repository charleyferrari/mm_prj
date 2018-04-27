d3.json('/api/max_income', json => {
  d3
    .select('#viz ul')
    .selectAll('li')
    .data(json.data)
    .enter()
    .append('li')
    .text(d => `${d.gender}: ${d.max_income}`);
});

// -----------------------------------------------------------------------
// Stacked Bar Chart
// -----------------------------------------------------------------------

// Define margins, heights and widths
let bar_margin = {
    top: 20,
    right: 20,
    bottom: 40,
    left: 60
  },
  bar_width = 960 - bar_margin.left - bar_margin.right,
  bar_height = 500 - bar_margin.top - bar_margin.bottom;

const bar_svg = d3
  .select('#bar')
  .append('svg')
  .attr('width', bar_width + bar_margin.left + bar_margin.right)
  .attr('height', bar_height + bar_margin.top + bar_margin.bottom)
  .append('g')
  .attr('transform', `translate(${bar_margin.left},${bar_margin.top})`);

// Predefine the div for the tooltips.
let bar_tooltip = d3
  .select('body')
  .append('div')
  .attr('class', 'toolTip');

// Helper function to map classes from the insurance_segment keys
const classFromKey = key => {
  const [first] = key.split(' ');
  return first == 'The' ? 'nest' : first.toLowerCase();
};

d3.json('/api/econ_api', json => {
  const x = d3
    .scaleBand()
    .range([0, bar_width])
    .domain(json.econ)
    .padding(0.1);

  const y = d3
    .scaleLinear()
    .range([bar_height, 0])
    .domain([0, json.max_y]);

  bar_legend = bar_svg
    .append('g')
    .attr('class', 'legend')
    .attr('transform', `translate(${7 * bar_width / 8}, ${bar_height / 12})`);

  // Add a trace and legend entry for each insurance segment
  let i = 0;
  Object.keys(json.data[0].cum)
    .reverse()
    .forEach(e => {
      if (e != 'economic_stability') {
        bar_svg
          .selectAll(`.${classFromKey(e)}`)
          .data(json.data)
          .enter()
          .append('rect')
          .attr('class', classFromKey(e))
          .attr('x', d => x(d.cum.economic_stability))
          .attr('width', x.bandwidth())
          .attr('y', d => y(d.cum[e]))
          .attr('height', d => bar_height - y(d.cum[e]))
          // Add display tooltips when hovering over bars
          .on('mouseover', d => {
            bar_tooltip
              .html(
                `Insurance Segment: ${e}<br/>
                  Economic Stability: ${d.val.economic_stability}<br/>
                  Count: ${d.val[e]}`
              )
              .style('opacity', 0.9)
              .style('left', `${d3.event.pageX}px`)
              .style('top', `${d3.event.pageY - 28}px`);
          })
          // And get rid of it on mouseout
          .on('mouseout', d => {
            bar_tooltip.style('opacity', 0);
          });

        bar_legend
          .append('rect')
          .attr('class', classFromKey(e))
          .attr('x', 0)
          .attr('y', i - 10)
          .attr('height', 11)
          .attr('width', 11);

        bar_legend
          .append('text')
          .text(e)
          .attr('transform', `translate(13, ${i})`)
          .attr('class', 'legend-text');

        i += 12;
      }
    });

  bar_svg
    .append('g')
    .attr('transform', `translate(0,${bar_height})`)
    .call(d3.axisBottom(x));

  bar_svg.append('g').call(d3.axisLeft(y));
});

// Add axis Labels
bar_svg
  .append('text')
  .attr('text-anchor', 'middle')
  .attr('transform', `translate(-40, ${bar_height / 2})rotate(-90)`)
  .attr('class', 'axis-label')
  .text('Count');

bar_svg
  .append('text')
  .attr('text-anchor', 'middle')
  .attr('transform', `translate(${bar_width / 2}, ${bar_height + 30})`)
  .attr('class', 'axis-label')
  .text('Economic Stability');

// -----------------------------------------------------------------------
// Box Plot
// -----------------------------------------------------------------------

// Define margins, heights and widths
let box_margin = {
    top: 20,
    right: 20,
    bottom: 30,
    left: 40
  },
  box_width = 960 - box_margin.left - box_margin.right,
  box_height = 500 - box_margin.top - box_margin.bottom,
  box_indiv_width = 30;

const box_svg = d3
  .select('#box')
  .append('svg')
  .attr('width', box_width + box_margin.left + box_margin.right)
  .attr('height', box_height + box_margin.top + box_margin.bottom)
  .append('g')
  .attr('transform', `translate(${box_margin.left},${box_margin.top})`);

d3.json('/api/box_api', json => {
  const x = d3
    .scalePoint()
    .domain(json.data.map(d => d.key))
    .rangeRound([0, box_width])
    .padding([0.5]);

  const y = d3
    .scaleLinear()
    .domain([json.max_y, json.min_y])
    .range([0, box_height]);

  // Draw the vertical lines covering IQR + 1.5*IQR in either direction
  box_svg
    .selectAll('.verticalLines')
    .data(json.data)
    .enter()
    .append('line')
    .attr('x1', d => x(d.key))
    .attr('y1', d => y(d.max))
    .attr('x2', d => x(d.key))
    .attr('y2', d => y(d.min))
    .attr('stroke', '#000')
    .attr('stroke-width', 1)
    .attr('fill', 'none');

  // draw rectangles for the boxes covering IQR
  box_svg
    .selectAll('rect')
    .data(json.data)
    .enter()
    .append('rect')
    .attr('width', box_indiv_width)
    .attr('height', d => y(d.p25) - y(d.p75))
    .attr('x', d => x(d.key) - box_indiv_width / 2)
    .attr('y', d => y(d.p75))
    .attr('class', d => classFromKey(d.key))
    .attr('stroke', '#000')
    .attr('stroke-width', 1);

  // Loop through the three horizontal lines (min, max, and median) to complete
  // the whiskers.
  ['max', 'med', 'min'].forEach(e => {
    box_svg
      .selectAll('.whiskers')
      .data(json.data)
      .enter()
      .append('line')
      .attr('x1', d => x(d.key) - box_indiv_width / 2)
      .attr('x2', d => x(d.key) + box_indiv_width / 2)
      .attr('y1', d => y(d[e]))
      .attr('y2', d => y(d[e]))
      .attr('stroke', '#000')
      .attr('stroke-width', 1)
      .attr('fill', 'none');
  });

  box_svg.append('g').call(d3.axisLeft(y));
  box_svg
    .append('g')
    .attr('transform', `translate(0,${box_height})`)
    .call(d3.axisBottom(x));
});
