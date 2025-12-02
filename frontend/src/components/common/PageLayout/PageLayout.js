import ParticleBackground from '../../dashboard/ParticleBackground/ParticleBackground';
import BackButton from '../BackButton/BackButton';
import './PageLayout.css';

function PageLayout({ children, showParticles = true, showBackButton = true }) {
  return (
    <div className="page">
      {showParticles && <ParticleBackground />}
      {showBackButton && <BackButton />}
      <div className="page-content">
        {children}
      </div>
    </div>
  );
}

export default PageLayout;

