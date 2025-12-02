import './Badge.css';

function Badge({ children, variant = 'gray' }) {
  return (
    <span className={`badge badge-${variant}`}>
      {children}
    </span>
  );
}

export default Badge;

