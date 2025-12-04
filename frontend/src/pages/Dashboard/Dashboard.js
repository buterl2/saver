import DashboardButton from '../../components/dashboard/DashboardButton/DashboardButton';
import ParticleBackground from '../../components/dashboard/ParticleBackground/ParticleBackground';
import { TbChartLine } from 'react-icons/tb';
import { TbBox } from 'react-icons/tb';
import { TbChartBar } from 'react-icons/tb';
import { TbBarcode } from 'react-icons/tb';
import './Dashboard.css';

function Dashboard() {
  return (
    <div className="App">
      <ParticleBackground />
      <div className='content'>
        <h1 className="title">CVNS Dashboard</h1>
        <div className='button-container'>
          <DashboardButton
            text='Picking Monitor'
            icon={<TbChartLine />}
            path='/picking'
          />
          <DashboardButton
            text='Packing Monitor'
            icon={<TbBox />}
            path='/packing'
          />
          <DashboardButton
            text='B-Flow Dashboard'
            icon={<TbChartBar />}
            path='/bflow'
          />
          <DashboardButton
            text='Barcode Generator'
            icon={<TbBarcode />}
            path='/barcode'
          />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

