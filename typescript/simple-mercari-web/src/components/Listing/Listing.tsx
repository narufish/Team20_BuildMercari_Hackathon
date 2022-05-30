import React, { useState } from 'react';

const server = process.env.API_URL || 'http://127.0.0.1:9000';

interface Prop {
  onListingCompleted?: () => void;
}

type formDataType = {
  name: string,
  category: string,
  image: string | File,
}

export const Listing: React.FC<Prop> = (props) => {
  const { onListingCompleted } = props;
  const initialState = {
    name: "",
    category: "",
    image: "",
  };
  const [values, setValues] = useState<formDataType>(initialState);

  const onValueChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValues({
      ...values, [event.target.name]: event.target.value,
    })
  };
  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValues({
      ...values, [event.target.name]: event.target.files![0],
    })
  };
  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const data = new FormData()
    data.append('item_name', values.name)
    data.append('category', values.category)
    data.append('image', values.image)
    data.append('item_state_id', 'null')
    data.append('delivery_id', 'null')
    data.append('price', 'null')
    data.append('description', 'null')

    fetch(server.concat('/drafts'), {
      method: 'POST',
      mode: 'cors',
      body: data,
    })
      .then(response => {
        console.log('POST status:', response.statusText);
        onListingCompleted && onListingCompleted();
      })
      .catch((error) => {
        console.error('POST error:', error);
      })
  };
  return (
    <div className='Listing'>
      <form onSubmit={onSubmit}>
        <label>Name:</label>
        <div>
          <input type='text' name='name' id='name' placeholder='name' onChange={onValueChange} required />
	</div>
  <label>Category:</label>
	<div>
          <input type='text' name='category' id='category' placeholder='category' onChange={onValueChange} required />
	</div>
  <label>Upload image:</label>
	<div> 
          <label id="button" htmlFor="image">
            <input type='file' name='image' id='image' onChange={onFileChange} required hidden />
            Choose file
          </label>
          <span></span>
	</div>
	<div>
          <button type='submit' id="button">List this item</button>
        </div>
      </form>
    </div>
  );
}