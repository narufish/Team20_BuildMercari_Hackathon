import React, { useState } from 'react';

interface Prop {
	onSelectCompleted?: () => void;
}

export const ToolBar: React.FC<Prop> = (props) => {
	const [selectMode, setSelectMode] = useState(true);
	
    function toggleSelect() {
		if (selectMode) {
			/* Replace button text, hide and empty checkboxes */
			setSelectMode(!selectMode);
		} else {
			/* Change button text to "Done", show checkboxes, show delete button */
			/* Show sorting handles (later) */
			setSelectMode(!selectMode);
		}
	};
	
	return (
		<header className='ToolBar'>
			<div className='TBarItem'>
			  <p>
				
			  </p>
			</div>
			<div className='Title'>
			  <p>
				<b>All Drafts</b>
			  </p>
			</div>
			<div className='TBarItem'>
			  <p>
				<button name='SelectButton' /*onClick={toggleSelect()}*/>Select</button>
			  </p>
			</div>
		</header>
	);
}