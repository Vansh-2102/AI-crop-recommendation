import React, { useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { marketAPI } from '../services/api';

const Market = () => {
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    commodity: 'Wheat',
    state: '',
    market: '',
    limit: 25,
    sort: 'modal_price',
    order: 'desc'
  });
  const [records, setRecords] = useState([]);
  const [source, setSource] = useState('');
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const fetchMarketData = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const { data } = await marketAPI.getPrices(filters);
      const recs = data.records || data.market_data || [];
      setRecords(recs);
      setSource(data.source || (data.records ? 'data.gov.in' : 'mock'));
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to fetch market data');
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
      </div>

      <div className="market-container">
        <form className="filter-form" onSubmit={fetchMarketData}>
          <div className="form-row">
            <div className="form-group">
              <label>Commodity</label>
              <input name="commodity" value={filters.commodity} onChange={handleChange} placeholder="e.g., Wheat" />
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
            <p>No records found.</p>
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
