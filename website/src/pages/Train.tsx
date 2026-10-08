import { PageHeading, Note } from '../components/ui';
import SetupGuide from '../components/SetupGuide';

export default function Train() {
  return <div className="container reading-page"><PageHeading eyebrow="YOUR TURN / REPRODUCE THE EXPERIMENT" title="Give the courier a new education." description="The real source, the actual commands, and a clean path from download to your own trained policy. Python handles the experiment; this website explains it." /><Note title="What you need"><p>Python 3.10+, a desktop environment for Pygame, and enough disk space for PyTorch. No GPU, paid service, or website backend is required. The setup below follows the verified Windows / PowerShell workflow.</p></Note><SetupGuide /></div>;
}
