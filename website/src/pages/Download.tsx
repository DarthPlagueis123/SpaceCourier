import { Link } from 'react-router-dom';
import downloads from '../generated/downloads.json';
import { PageHeading, Note, CodeBlock, Arrow } from '../components/ui';

const descriptions: Record<string,{title:string;tag:string;description:string}> = {
  'space-courier-game.zip':{title:'The arcade game',tag:'PYTHON / PYGAME',description:'The original human-playable game, handmade pixel art, and synthesized sound. Install Pygame and run locally.'},
  'space-courier-source.zip':{title:'The complete source',tag:'GAME + AI + WEBSITE',description:'Game and trainer code, the saved model and checkpoints, actual data, tests, and this React website’s source.'},
  'space-courier-dqn.pth':{title:'The trained model',tag:'PYTORCH CHECKPOINT',description:'The selected 150,000-decision Double DQN, with online and target weights, optimizer state, and configuration.'},
  'training-history.csv':{title:'The real training data',tag:'1,059 EPISODES / CSV',description:'Scores, rewards, moving averages, loss, epsilon, duration, and checkpoint associations from the full run.'},
  'model-metadata.json':{title:'Model metadata',tag:'CONFIGURATION / JSON',description:'Exact inputs, actions, architecture, reward values, hyperparameters, and measured evaluation statistics.'},
  'evaluation-results.json':{title:'The evaluation records',tag:'100 GAMES / JSON',description:'Aggregate selected-model performance and each held-out game, including seed, score, duration, and truncation.'},
};
function size(bytes:number) { return bytes>1e6?`${(bytes/1e6).toFixed(1)} MB`:`${(bytes/1e3).toFixed(0)} KB`; }

export default function Download() {
  return <div className="container wide-page"><PageHeading eyebrow="TAKE THE PROJECT WITH YOU" title="Not just a story. The source." description="Download the actual game, learned weights, and evidence behind this guide. Every file below is included and ready to inspect." /><div className="download-grid">{downloads.map(file=>{const description=descriptions[file.filename];return <article className="download-card" key={file.filename}><span className="download-icon" aria-hidden="true">↓</span><span className="micro">{description.tag}</span><h2>{description.title}</h2><p>{description.description}</p><a className="button" href={file.url} download>Download <span>{size(file.bytes)}</span><Arrow direction="down" /></a><details><summary>File integrity</summary><p className="small">SHA-256</p><code className="checksum">{file.sha256}</code></details></article>;})}</div><Note title="This is a Python game, not a browser executable"><p>No packaged Windows .exe or public Git repository currently exists. The game download contains runnable Python source. Browser AI playback uses genuine recordings; live inference runs locally with PyTorch.</p></Note><section className="download-quickstart"><div><span className="micro">PLAY IN TWO COMMANDS</span><h2>Unzip. Install. Launch.</h2><p>Open a terminal inside the extracted <code>pixel-panic</code> folder.</p></div><CodeBlock code="python -m pip install -r requirements.txt\npython main.py" filename="Terminal / human game" language="bash" /></section><div className="page-bottom-links"><Link className="button" to="/train">Train it yourself <Arrow /></Link><Link className="text-link" to="/about">Explore the project structure <Arrow /></Link></div></div>;
}
