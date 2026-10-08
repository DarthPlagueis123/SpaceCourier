import { Link } from 'react-router-dom';
import { PageHeading, Arrow } from '../components/ui';
import CheckpointPlayer from '../components/CheckpointPlayer';

export default function Watch() {
  return <div className="container wide-page"><PageHeading eyebrow="05 / WATCH IT LEARN" title="Same ship. Different experience." description="Explore five genuine saved policies playing the original game on the same asteroid sequence. Learning is useful—and less tidy than a highlight reel." /><CheckpointPlayer /><div className="page-bottom-links"><Link className="button" to="/results">Inspect the 100-game results <Arrow /></Link><Link className="text-link" to="/train">Run live inference yourself <Arrow /></Link></div></div>;
}
