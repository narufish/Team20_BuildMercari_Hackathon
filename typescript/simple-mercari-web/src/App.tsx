import { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import './App.css';
import { ItemList } from './components/ItemList';
import { Listing } from './components/Listing';
import { ToolBar } from './components/ToolBar';

function App() {
  // reload ItemList after Listing complete
  const [reload, setReload] = useState(true);
  const [selectMode, setSelectMode] = useState({
    toggled: false,
    buttonText: 'Edit',
  });

  return (
    <div>
      <ToolBar selectMode={selectMode} onSelectToggled={() => setReload(true)} />
      <div>
        <Listing onListingCompleted={() => setReload(true)} />
      </div>
      <div>
        <ItemList reload={reload} onLoadCompleted={() => setReload(false)} selectModeOn={selectMode.toggled} />
      </div>
    </div>
  )
}

export default App;