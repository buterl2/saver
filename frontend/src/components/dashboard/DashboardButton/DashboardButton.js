import { Link } from 'react-router-dom';
import './DashboardButton.css';

function DashboardButton({ text, icon, path }) {
    return (
        <Link to={path} className='dashboard-button'>
            <div className='button-content'>
                {icon}
                <span>{text}</span>
            </div>
        </Link>
    );
}

export default DashboardButton;

