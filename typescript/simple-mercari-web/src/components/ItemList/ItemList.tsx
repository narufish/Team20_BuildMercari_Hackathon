import React, { useEffect, useState } from 'react';

interface Item {
  id: number;
  name: string;
  category: string;
  image: string;
};

const server = process.env.API_URL || 'http://127.0.0.1:9000';
// const placeholderImage = process.env.PUBLIC_URL + '/logo192.png';

interface Prop {
  reload?: boolean;
  onLoadCompleted?: () => void;
  selectModeOn?: boolean;
  checkList?: number[];
  handleClick?:  (id: number, checked: boolean) => void;
}

export const ItemList: React.FC<Prop> = (props) => {
  const { reload = true, onLoadCompleted, selectModeOn, checkList = [], handleClick } = props;
  const [items, setItems] = useState<Item[]>([])
  const fetchItems = () => {
    fetch(server.concat('/items'),
      {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
      })
      .then(response => response.json())
      .then(data => {
        console.log('GET success:', data);
        setItems(data.items);
        onLoadCompleted && onLoadCompleted();
      })
      .catch(error => {
        console.error('GET error:', error)
      })
  }

  useEffect(() => {
    if (reload) {
      fetchItems();
    }
  }, [reload]);
  
  const checkVis = {
    display: (selectModeOn ? 'block' : 'none'),
  };
  
  return (
    <div className='ItemGrid'>
      {items.map((item) => {
        const isChecked: boolean = checkList.includes(item.id);
        return (
          <div key={item.id} className='ItemList'>
            <input 
              className='Selector'
              id={String(item.id)}
              name={item.name}
              type='checkbox'
              onChange={() => handleClick?.(item.id, !isChecked)}
              defaultChecked={false}
              style={checkVis}
            />
            <img src={server + "/image/" + item.image} />
            <p>
              <span>Name: {item.name}</span>
              <br />
              <span>Category: {item.category}</span>
            </p>
          </div>
        )
      })}
    </div>
  )
};
