import { useState } from 'react';
import './App.css';
import { ItemList } from './components/ItemList';
import { Listing } from './components/Listing';

function App() {
  // reload ItemList after Listing complete
  const [reload, setReload] = useState(true);
  /* function toggleSelect() {
    ItemList.all
  } */
  return (
    <div>
      <header className='NavBar'>
        <div className='NavItem'>
          <p>
            
          </p>
        </div>
        <div className='Title'>
          <p>
            <b>All Drafts</b>
          </p>
        </div>
        <div className='NavItem'>
          <p>
            <button /*onClick={toggleSelect}*/>Select</button>
          </p>
        </div>
      </header>
      {/* <div>
        <Listing onListingCompleted={() => setReload(true)} />
      </div> */}
      <div>
        <ItemList reload={reload} onLoadCompleted={() => setReload(false)} />
      </div>
    </div>
  )
}

export default App;