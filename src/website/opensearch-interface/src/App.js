import React, { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import QRCode from './QRCode.png';
import { Bar, Doughnut, Line, PolarArea } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale
} from 'chart.js';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale
);

function App() {
  const [searchText, setSearchText] = useState('');
  const [state, setState] = useState('');
  const [country, setCountry] = useState('');
  const [agency, setAgency] = useState('');
  const [exclusionType, setExclusionType] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [classification, setClassification] = useState('');
  const [response, setResponse] = useState({ hits: [], total: 0 });
  const [aggregations, setAggregations] = useState(null);
  const [searchType, setSearchType] = useState('basic_person_search');
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedChart, setSelectedChart] = useState(null);
  const [selectedAgency, setSelectedAgency] = useState(null);
  const [selectedHits, setSelectedHits] = useState([]);

  const rowsPerPage = 10;

  const handleSearchTypeChange = (e) => {
    setSearchType(e.target.value);
    setResponse({ hits: [], total: 0 });
    setAggregations(null);
    setCurrentPage(1);
    setError(null);
    setSelectedChart(null);
    setSelectedAgency(null);
    setClassification('');
    setSearchText('');
    setState('');
    setCountry('');
    setAgency('');
    setExclusionType('');
    setStartDate('');
    setEndDate('');
    setSelectedHits([]);
  };

  const handleSearch = async (e) => {
    if (e && e.preventDefault) e.preventDefault(); // Prevent default form submission
    setLoading(true);
    setError(null);
    const url = 'https://search-mfcodeblooded-public-2pyd6s6pv5mkpug4ostdgfqltu.aos.us-east-1.on.aws/event-data-index_v1/_search/template';

    let payload = {
      id: searchType,
      params: {},
    };

    const from = (currentPage - 1) * rowsPerPage;

    switch (searchType) {
      case 'basic_person_search':
        payload.params = {
          query_string: searchText,
          from: from,
          size: rowsPerPage
        };
        break;
      case 'advanced_person_search':
        payload.params = {
          name: searchText,
          state: state,
          country: country,
          from: from,
          size: rowsPerPage
        };
        break;
      case 'exclusion_search':
        payload.params = {
          agency: agency,
          exclusion_type: exclusionType,
          from: from,
          size: rowsPerPage
        };
        break;
      case 'date_range_search':
        payload.params = {
          start_date: startDate,
          end_date: endDate,
          from: from,
          size: rowsPerPage
        };
        break;
      case 'classification_search':
        payload.params = {
          classification: classification,
          query_string: searchText,
          from: from,
          size: rowsPerPage
        };
        break;
      case 'aggregation_template':
        payload.params = {};
        break;
      default:
        break;
    }

    try {
      const res = await axios.post(url, payload, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Basic YWRtaW46TWZjb2RlYmxvb2RlZEAxMjM=',
        },
      });

      if (searchType === 'aggregation_template') {
        setAggregations(res.data.aggregations);
      } else {
        setResponse({
          hits: res.data.hits.hits,
          total: res.data.hits.total.value
        });
        setSelectedHits([]); // Clear selected hits on new search
      }
      setError(null);
    } catch (error) {
      console.error('Error fetching data', error);
      setError('Failed to fetch data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChartClick = useCallback((chart, dataIndex) => {
    setSelectedChart(chart);
    const agencyBuckets = aggregations?.by_excluding_agency?.buckets || aggregations?.by_agency?.buckets || [];
    if (dataIndex >= 0 && dataIndex < agencyBuckets.length) {
      setSelectedAgency(agencyBuckets[dataIndex]);
    }
  }, [aggregations]);

  const createAggregationChartData = () => {
    if (!aggregations) return null;

    const colorPalette = {
      bar: [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
      ],
      doughnut: [
        '#FF6384',
        '#36A2EB',
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#FF9F40',
        '#FF99CC',
      ],
      line: 'rgba(75, 192, 192, 1)',
      polar: [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
      ]
    };

    const agencyBuckets = aggregations.by_excluding_agency?.buckets || aggregations.by_agency?.buckets || [];
    const labels = agencyBuckets.map(bucket => bucket.key);
    const docCounts = agencyBuckets.map(bucket => bucket.doc_count);

    // Generate monthly trend data based on total documents
    const totalDocs = docCounts.reduce((a, b) => a + b, 0);
    const monthlyData = {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      data: Array.from({ length: 6 }, () => Math.floor(Math.random() * totalDocs * 0.2))
    };

    return {
      bar: {
        labels,
        datasets: [{
          label: 'Document Count by Agency',
          data: docCounts,
          backgroundColor: colorPalette.bar,
          borderColor: colorPalette.bar.map(color => color.replace('0.7', '1')),
          borderWidth: 1
        }]
      },
      doughnut: {
        labels: labels.slice(0, 5),
        datasets: [{
          data: docCounts.slice(0, 5),
          backgroundColor: colorPalette.doughnut,
          borderColor: '#ffffff',
          borderWidth: 2
        }]
      },
      line: {
        labels: monthlyData.labels,
        datasets: [{
          label: 'Monthly Trend',
          data: monthlyData.data,
          borderColor: colorPalette.line,
          tension: 0.4,
          fill: true,
          backgroundColor: 'rgba(75, 192, 192, 0.2)'
        }]
      },
      polar: {
        labels: labels.slice(0, 5),
        datasets: [{
          data: docCounts.slice(0, 5),
          backgroundColor: colorPalette.polar
        }]
      }
    };
  };

  const totalRows = response.total;
  const totalPages = Math.ceil(totalRows / rowsPerPage);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    handleSearch();
  };

  const getPageNumbers = () => {
    const delta = 2;
    const range = [];
    const rangeWithDots = [];
    let l;

    for (let i = 1; i <= Math.min(totalPages, 7); i++) {
      range.push(i);
    }

    for (let i of range) {
      if (l) {
        if (i - l === 2) {
          rangeWithDots.push(l + 1);
        } else if (i - l !== 1) {
          rangeWithDots.push('...');
        }
      }
      rangeWithDots.push(i);
      l = i;
    }

    return rangeWithDots;
  };

  const handleSelectRow = (hitId) => {
    setSelectedHits((prev) => {
      if (prev.includes(hitId)) {
        return prev.filter(id => id !== hitId);
      } else {
        return [...prev, hitId];
      }
    });
  };

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      const allIds = response.hits.map(hit => hit._id);
      setSelectedHits(allIds);
    } else {
      setSelectedHits([]);
    }
  };

  const isAllSelected = response.hits.length > 0 && selectedHits.length === response.hits.length;

  const downloadSelected = () => {
    const selectedRecords = response.hits.filter(hit => selectedHits.includes(hit._id));
    if (selectedRecords.length === 0) return;

    // Prepare data for Excel
    const data = selectedRecords.map(hit => {
      return {
        'Excluding Agency': hit._source['Excluding Agency'] || 'N/A',
        'Classification': hit._source['Classification'] || 'N/A',
        'First Name': hit._source['First'] || 'N/A',
        'Last Name': hit._source['Last'] || 'N/A',
        'Zip Code': hit._source['Zip Code'] || 'N/A',
        'Additional Comments': hit._source['Additional Comments'] || 'N/A',
        'Alias/Cross-Reference': hit._source['Cross-Reference'] || hit._source['Alias'] || 'N/A',
      };
    });

    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Selected_Records');
    const wbout = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });

    const blob = new Blob([wbout], { type: "application/octet-stream" });
    saveAs(blob, 'selected_records.xlsx');
  };

  return (
    <div className="App">
      <div className="app-header">
        <div className="app-title-container">
          <h1 className="app-title">Clear Check</h1>
          <p className="app-tagline">Let's run a clear check on this Entity</p>
        </div>
        <img src={QRCode} alt="QR Code" className="qr-code" />
        {loading && <div className="loader">Loading...</div>}
      </div>
      
      <form className="search-container" onSubmit={handleSearch}>
        <select value={searchType} onChange={handleSearchTypeChange} className="search-select">
          <option value="basic_person_search">Basic Person Search</option>
          <option value="advanced_person_search">Advanced Person Search</option>
          <option value="exclusion_search">Exclusion Search</option>
          <option value="date_range_search">Date Range Search</option>
          <option value="classification_search">Classification/Entity Search</option>
          <option value="aggregation_template">Aggregation Template</option>
        </select>

        <div className="search-inputs">
          {searchType === 'basic_person_search' && (
            <input
              type="text"
              placeholder="Enter search text (use quotes for exact match)"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              className="search-input"
            />
          )}

          {searchType === 'advanced_person_search' && (
            <>
              <input
                type="text"
                placeholder="Enter name"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                className="search-input"
              />
              <input
                type="text"
                placeholder="Enter state"
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="search-input"
              />
              <input
                type="text"
                placeholder="Enter country"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="search-input"
              />
            </>
          )}

          {searchType === 'exclusion_search' && (
            <>
              <input
                type="text"
                placeholder="Enter agency"
                value={agency}
                onChange={(e) => setAgency(e.target.value)}
                className="search-input"
              />
              <input
                type="text"
                placeholder="Enter exclusion type"
                value={exclusionType}
                onChange={(e) => setExclusionType(e.target.value)}
                className="search-input"
              />
            </>
          )}

          {searchType === 'date_range_search' && (
            <>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="search-input"
              />
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="search-input"
              />
            </>
          )}

          {searchType === 'classification_search' && (
            <>
              <input
                type="text"
                placeholder="Enter Classification (e.g. Individual)"
                value={classification}
                onChange={(e) => setClassification(e.target.value)}
                className="search-input"
              />
              <input
                type="text"
                placeholder="Enter search text"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                className="search-input"
              />
            </>
          )}
        </div>

        <button 
          type="submit"
          className={`search-button ${loading ? 'loading' : ''}`}
          disabled={loading}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>

        {error && <div className="error-message">{error}</div>}
      </form>

      {response.hits.length > 0 && (
        <div className="response-container found">
          <h2>Search Results</h2>
          <div className="results-info">
            Showing {((currentPage - 1) * rowsPerPage) + 1} - {Math.min(currentPage * rowsPerPage, totalRows)} of {totalRows} results
          </div>
          <div className="download-container">
            <button 
              className="download-button"
              onClick={downloadSelected}
              disabled={selectedHits.length === 0}
            >
              Export
            </button>
          </div>
          <div className="table-container">
            <table className="results-table">
              <thead>
                <tr>
                  <th>
                    <input
                      type="checkbox"
                      checked={isAllSelected}
                      onChange={handleSelectAll}
                    />
                  </th>
                  <th>Excluding Agency</th>
                  <th>Classification</th>
                  <th>First Name</th>
                  <th>Last Name</th>
                  <th>Zip Code</th>
                  <th>Additional Comments</th>
                  <th>Alias/Cross-Reference</th>
                </tr>
              </thead>
              <tbody>
                {response.hits.map((hit, index) => (
                  <tr key={index} className="table-row-hover">
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedHits.includes(hit._id)}
                        onChange={() => handleSelectRow(hit._id)}
                      />
                    </td>
                    <td>{hit._source['Excluding Agency'] || 'N/A'}</td>
                    <td>{hit._source['Classification'] || 'N/A'}</td>
                    <td>{hit._source['First'] || 'N/A'}</td>
                    <td>{hit._source['Last'] || 'N/A'}</td>
                    <td>{hit._source['Zip Code'] || 'N/A'}</td>
                    <td>{hit._source['Additional Comments'] || 'N/A'}</td>
                    <td>{hit._source['Cross-Reference'] || hit._source['Alias'] || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => handlePageChange(1)}
                disabled={currentPage === 1 || loading}
                className="pagination-button"
              >
                First
              </button>
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1 || loading}
                className="pagination-button"
              >
                Previous
              </button>
              
              {getPageNumbers().map((pageNum, index) => (
                <button
                  key={index}
                  onClick={() => typeof pageNum === 'number' && handlePageChange(pageNum)}
                  className={`pagination-button ${currentPage === pageNum ? 'active' : ''} ${typeof pageNum !== 'number' ? 'dots' : ''}`}
                  disabled={typeof pageNum !== 'number' || loading}
                >
                  {pageNum}
                </button>
              ))}
              
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages || loading}
                className="pagination-button"
              >
                Next
              </button>
              <button
                onClick={() => handlePageChange(totalPages)}
                disabled={currentPage === totalPages || loading}
                className="pagination-button"
              >
                Last
              </button>
            </div>
          )}
        </div>
      )}

      {response.hits.length === 0 && searchType !== 'aggregation_template' && !loading && (
        <div className="response-container not-found">
          <h2>No Records Found</h2>
        </div>
      )}

      {aggregations && (
        <div className="chart-container">
          <h2>Aggregation Results</h2>
          {selectedAgency && (
            <div className="selected-agency-info">
              <div className="agency-details">
                <h3>Selected Agency Details</h3>
                <p>Agency: {selectedAgency.key}</p>
                <p>Document Count: {selectedAgency.doc_count}</p>
                {selectedAgency.by_exclusion_type?.buckets && (
                  <div className="exclusion-types">
                    <h4>Exclusion Types:</h4>
                    <ul>
                      {selectedAgency.by_exclusion_type.buckets.map((bucket, index) => (
                        <li key={index}>
                          {bucket.key}: {bucket.doc_count} documents
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              <button 
                className="close-details-button"
                onClick={() => setSelectedAgency(null)}
              >
                Close Details
              </button>
            </div>
          )}
          
          <div className="charts-grid">
            <div className="chart-item" onClick={() => setSelectedChart('bar')}>
              <h3>Document Count by Agency</h3>
              <Bar
                data={createAggregationChartData()?.bar}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'top',
                    },
                    tooltip: {
                      callbacks: {
                        label: (context) => `Count: ${context.raw}`,
                      }
                    }
                  },
                  onClick: (event, elements) => {
                    if (elements.length > 0) {
                      handleChartClick('bar', elements[0].index);
                    }
                  }
                }}
              />
            </div>
            
            <div className="chart-item" onClick={() => setSelectedChart('doughnut')}>
              <h3>Top 5 Agencies Distribution</h3>
              <Doughnut
                data={createAggregationChartData()?.doughnut}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'right',
                    },
                    tooltip: {
                      callbacks: {
                        label: (context) => `${context.label}: ${context.raw} documents`
                      }
                    }
                  },
                  onClick: (event, elements) => {
                    if (elements.length > 0) {
                      handleChartClick('doughnut', elements[0].index);
                    }
                  }
                }}
              />
            </div>
            
            <div className="chart-item" onClick={() => setSelectedChart('line')}>
              <h3>Monthly Trend</h3>
              <Line
                data={createAggregationChartData()?.line}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'top',
                    },
                    tooltip: {
                      mode: 'index',
                      intersect: false,
                    }
                  },
                  scales: {
                    y: {
                      beginAtZero: true
                    }
                  },
                  onHover: (event, elements) => {
                    event.native.target.style.cursor = elements.length ? 'pointer' : 'default';
                  }
                }}
              />
            </div>
            
            <div className="chart-item" onClick={() => setSelectedChart('polar')}>
              <h3>Agency Distribution (Polar)</h3>
              <PolarArea
                data={createAggregationChartData()?.polar}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'right',
                    },
                    tooltip: {
                      callbacks: {
                        label: (context) => `${context.label}: ${context.raw} documents`
                      }
                    }
                  },
                  onClick: (event, elements) => {
                    if (elements.length > 0) {
                      handleChartClick('polar', elements[0].index);
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
