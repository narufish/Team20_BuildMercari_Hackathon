import React, { useState } from 'react';

interface Prop {
	onSelectToggled?: () => void;
	selectMode: {
		toggled: boolean,
		buttonText: string,
	};
	confirmDelete?: () => void;
}

export const ToolBar: React.FC<Prop> = (props) => {
	const { selectMode, onSelectToggled, confirmDelete } = props;
	
    function toggleSelect() {
		if (selectMode.toggled) {
			/* Hide and empty checkboxes */
			selectMode.toggled = false;
			selectMode.buttonText = 'Edit';
			onSelectToggled && onSelectToggled();
		} else {
			/* Show checkboxes, show delete button */
			/* Show sorting handles (later) */
			selectMode.toggled = true;
			selectMode.buttonText = 'Done';
			onSelectToggled && onSelectToggled();
		}
	};
	
	const deleteVis = {
		display: (selectMode.toggled ? 'table-cell' : 'none'),
	};
	
	return (
		<header className='ToolBar'>
			<div className='TBarItem'>
			  <p>
				<button name='DeleteButton' onClick={confirmDelete} style={deleteVis} >Delete</button>
			  </p>
			</div>
			<div className='Title'>
			  <p>
				<b>All Drafts</b>
			  </p>
			</div>
			<div className='TBarItem'>
			  <p>
				<button name='SelectButton' onClick={toggleSelect} >{selectMode.buttonText}</button>
			  </p>
			</div>
		</header>
	);
}