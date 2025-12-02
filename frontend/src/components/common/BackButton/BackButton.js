import { Link } from 'react-router-dom';
import { TbArrowLeft } from 'react-icons/tb';
import './BackButton.css';

function BackButton({ to = '/' }) {
  return (
    <Link to={to} className="back-button">
      <TbArrowLeft />
      <span>Back</span>
    </Link>
  );
}

export default BackButton;

