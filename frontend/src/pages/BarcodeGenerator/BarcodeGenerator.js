import { useState } from 'react';
import { printBarcode } from '../../services/api';
import { PRINTERS } from '../../utils/constants';
import PageLayout from '../../components/common/PageLayout/PageLayout';
import './BarcodeGenerator.css';

function BarcodeGenerator() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [printer, setPrinter] = useState(PRINTERS[0]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username || !password) {
      setMessage('Please fill in all fields');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      await printBarcode({
        username: username,
        password: password,
        printer: printer
      });
      setMessage('✓ Barcode sent to printer!');
      setUsername('');
      setPassword('');
      setTimeout(() => setMessage(''), 5000);
    } catch (error) {
      console.error('Error:', error);
      setMessage(`✗ ${error.message || 'Failed to print barcode'}`);
      setTimeout(() => setMessage(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageLayout>
      <h1 className="page-title">Barcode Generator</h1>
      
      <div className="barcode-form-container">
        <form onSubmit={handleSubmit}>
          <div className="barcode-form-field">
            <label className="barcode-form-label">
              Username:
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="barcode-form-input"
            />
          </div>

          <div className="barcode-form-field">
            <label className="barcode-form-label">
              Password:
            </label>
            <input
              type="text"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="barcode-form-input"
            />
          </div>

          <div className="barcode-form-field">
            <label className="barcode-form-label">
              Select Printer:
            </label>
            <select
              value={printer}
              onChange={(e) => setPrinter(e.target.value)}
              className="barcode-form-select"
            >
              {PRINTERS.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`barcode-form-button ${loading ? 'loading' : ''}`}
          >
            {loading ? 'Printing...' : 'Print Barcode'}
          </button>
        </form>

        {message && (
          <div className={`barcode-message ${message.includes('✓') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}
      </div>
    </PageLayout>
  );
}

export default BarcodeGenerator;

