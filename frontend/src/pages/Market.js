import React, { useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { marketAPI } from '../services/api';

const Market = () => {
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    commodity: 'Apple',
    state: '',
    market: '',
    limit: 25,
    sort: 'modal_price',
    order: 'desc'
  });
  const [records, setRecords] = useState([]);
  const [source, setSource] = useState('');
  const [error, setError] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check login status on component mount
  React.useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsLoggedIn(!!token);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const fetchMarketData = async (e) => {
    if (e) e.preventDefault();
    
    // Check if user is logged in
    if (!isLoggedIn) {
      setError('Please log in to view market data.');
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      console.log('Fetching market data with filters:', filters);
      const { data } = await marketAPI.getPrices(filters);
      console.log('Market API response:', data);
      
      // Handle both data formats from backend
      let recs = [];
      if (data.records) {
        // Live data from data.gov.in
        recs = data.records;
      } else if (data.market_data) {
        // Mock data format - convert to table format
        recs = data.market_data.map(item => ({
          arrival_date: new Date().toISOString().split('T')[0],
          state: 'Sample State',
          district: 'Sample District', 
          market: 'Sample Market',
          commodity: item.crop,
          variety: 'Standard',
          min_price: Math.round(item.current_price * 0.9),
          max_price: Math.round(item.current_price * 1.1),
          modal_price: item.current_price
        }));
      }
      
      console.log('Records found:', recs.length);
      console.log('Sample record:', recs[0]);
      
      setRecords(recs);
      setSource(data.source || (data.records ? 'data.gov.in' : 'mock'));
    } catch (err) {
      console.error('Market API error:', err);
      if (err?.response?.status === 401) {
        setError('Please log in to view market data.');
      } else {
        setError(err?.response?.data?.error || 'Failed to fetch market data');
      }
      setRecords([]);
      setSource('');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchMarketData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="market">
      <div className="page-header">
        <h1>Market Prices</h1>
        <p>Current crop prices and market trends</p>
        {!isLoggedIn && (
          <div className="login-warning">
            <span>⚠️ Please log in to view market data.</span>
          </div>
        )}
      </div>

      <div className="market-container">
        <form className="filter-form" onSubmit={fetchMarketData}>
          <div className="form-row">
            <div className="form-group">
              <label>Commodity</label>
              <input name="commodity" value={filters.commodity} onChange={handleChange} placeholder="e.g., Apple, Rice, Potato" />
            </div>
            <div className="form-group">
              <label>State</label>
              <input name="state" value={filters.state} onChange={handleChange} placeholder="e.g., Maharashtra" />
            </div>
            <div className="form-group">
              <label>Market</label>
              <input name="market" value={filters.market} onChange={handleChange} placeholder="e.g., Mumbai" />
            </div>
            <div className="form-group">
              <label>Limit</label>
              <input name="limit" type="number" min="1" max="100" value={filters.limit} onChange={handleChange} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Sort By</label>
              <select name="sort" value={filters.sort} onChange={handleChange}>
                <option value="modal_price">Modal Price</option>
                <option value="max_price">Max Price</option>
                <option value="min_price">Min Price</option>
                <option value="commodity">Commodity</option>
                <option value="market">Market</option>
                <option value="state">State</option>
                <option value="arrival_date">Arrival Date</option>
              </select>
            </div>
            <div className="form-group">
              <label>Order</label>
              <select name="order" value={filters.order} onChange={handleChange}>
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
            </div>
            <div className="form-actions">
              <button type="submit" disabled={loading}>{loading ? 'Loading…' : 'Search'}</button>
            </div>
          </div>
        </form>

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        <div className="results-section">
          <h2>Results {source ? `(${source})` : ''}</h2>
          {records.length === 0 ? (
            <div className="no-data-message">
              <p>No records found for the selected filters.</p>
              <p><strong>Tips:</strong></p>
              <ul>
                <li>Try searching for "Apple", "Rice", or "Potato" - these are commonly available</li>
                <li>Leave commodity field empty to see all available data</li>
                <li>Check if you're logged in to access live data</li>
              </ul>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Arrival Date</th>
                    <th>State</th>
                    <th>District</th>
                    <th>Market</th>
                    <th>Commodity</th>
                    <th>Variety</th>
                    <th>Min</th>
                    <th>Max</th>
                    <th>Modal</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((r, idx) => (
                    <tr key={idx}>
                      <td>{r.arrival_date || '-'}</td>
                      <td>{r.state || '-'}</td>
                      <td>{r.district || '-'}</td>
                      <td>{r.market || '-'}</td>
                      <td>{r.commodity || r.crop || '-'}</td>
                      <td>{r.variety || '-'}</td>
                      <td>{r.min_price ?? '-'}</td>
                      <td>{r.max_price ?? '-'}</td>
                      <td>{r.modal_price ?? '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Market;
