import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/600.css';
import Dashboard from './pages/Dashboard/Dashboard';
import PickingMonitor from './pages/PickingMonitor/PickingMonitor';
import PackingMonitor from './pages/PackingMonitor/PackingMonitor';
import BFlowDashboard from './pages/BFlowDashboard/BFlowDashboard';
import BarcodeGenerator from './pages/BarcodeGenerator/BarcodeGenerator';
import DataUsers from './pages/DataUsers/DataUsers';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/picking" element={<PickingMonitor />} />
        <Route path="/packing" element={<PackingMonitor />} />
        <Route path="/bflow" element={<BFlowDashboard />} />
        <Route path="/barcode" element={<BarcodeGenerator />} />
        <Route path="/data_users" element={<DataUsers />} />
      </Routes>
    </Router>
  );
}

export default App;
