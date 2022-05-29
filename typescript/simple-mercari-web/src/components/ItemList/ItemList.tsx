import React, { useEffect, useState } from 'react';

interface Item {
  id: number;
  name: string;
  category: string;
  image: string;
  description: string;
  delivery: string;
  price: number;
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
    fetch(server.concat('/drafts'),
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
        setItems(data["draft items"]);
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
        function completeCheck(value: string | number) {
          if (value) {
            return 'IndicatorOn';
          }
          return 'IndicatorOff';
        }
        return (
          <div key={item.id} className='ItemList'>
            <div className='ItemInfo'>
              <input 
                className='Selector'
                id={String(item.id)}
                name={item.name}
                type='checkbox'
                onChange={() => handleClick?.(item.id, !isChecked)}
                defaultChecked={false}
                style={checkVis}
              />
              <img src={server + "/draft_image/" + item.image} />
              <p>
                <span>Name: {item.name}</span>
                <br />
                <span>Category: {item.category}</span>
              </p>
            </div>
            <div className='ProgressBar'>
              <div className='TitleRow'>
                <div className='ProgressTitle'>Image</div>
                <div className='ProgressTitle'>Info</div>
                <div className='ProgressTitle'>Description</div>
                <div className='ProgressTitle'>Shipping</div>
                <div className='ProgressTitle'>Price</div>
              </div>
              <div className='IndicatorRow'>
                <div className={completeCheck(item.image)}></div>
                <div className={completeCheck(item.category)}></div>
                <div className={completeCheck(item.description)}></div>
                <div className={completeCheck(item.delivery)}></div>
                <div className={completeCheck(item.price)}></div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
};
