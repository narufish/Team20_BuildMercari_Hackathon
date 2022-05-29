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
  const [isCheck, setIsCheck] = useState<number[]>([]);
  const server = process.env.API_URL || 'http://127.0.0.1:9000';
    
  function confirmDelete() {
    if (window.confirm("Do you want to delete the selected items?")) {
      console.log("Deleting items: " + isCheck);
      /* API request to delete each item */
      
      isCheck.forEach( x => {
        fetch(server.concat('/drafts/' + x), {
          method: 'DELETE',
          mode: 'cors'
        })
          .then(response => {
            console.log('DELETE status:', response.statusText);
            setSelectMode({
              toggled: false,
              buttonText: 'Edit',
            });
            setIsCheck([]);
            setReload(true);
          })
          .catch((error) => {
            console.error('POST error:', error);
          })
        }
      )
    }
  };
  
  function newChange(id: number, checked: boolean) {
    if (checked) {
      setIsCheck([...isCheck, id]);
    } else {
      setIsCheck(isCheck.filter(item => item !== id));
    }
  }

  return (
    <div>
      <ToolBar selectMode={selectMode} onSelectToggled={() => setReload(true)} confirmDelete={confirmDelete} />
      <div>
        <Listing onListingCompleted={() => setReload(true)} />
      </div>
      <div>
        <ItemList
          reload={reload}
          onLoadCompleted={ () => setReload(false) }
          selectModeOn={selectMode.toggled}
          checkList={isCheck}
          handleClick={ (id: number, checked: boolean) => newChange(id, checked) } />
      </div>
    </div>
  )
};

export default App;