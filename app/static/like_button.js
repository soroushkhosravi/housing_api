'use strict';
function Country(props) {
	return React.createElement(
		'div',
		{className: "container"},
		React.createElement(
			'h2',
			{className: "country-name"},
			`Country Name: ${props.name}`
			),
		React.createElement(
			'p',
			{className: "capital"},
			`Capital: ${props.capital}`
		),
		React.createElement(
		'p',
		{className: "population"},
		`Population: ${props.population}`
		)
	);
}

class Button extends React.Component {
	render() {
		const name = this.props.name
		return React.createElement('button', {className: 'btn btn-primary'}, 'I am a ' + name);
	}
}

class ShowCurrentUser extends React.Component {
	constructor(props) {
		super(props);
		this.state = {clicked: false}
		this.handleClick = this.handleClick.bind(this)
		this.handleUnClick = this.handleUnClick.bind(this)
	}
	handleClick(){
	// Changing state when we click on the element.
	this.setState({clicked : true})
	}

	handleUnClick(){
	// Changing state when we click on the element.
	this.setState({clicked : false})
	}
	render(){
		const clicked = this.state.clicked;
		if (clicked === false) {
			return React.createElement(
				'button', {className: 'btn btn-primary', onClick: this.handleClick}
				, 'I am not clicked')
			} else {
				return React.createElement(
					'button',
					{className: 'btn btn-danger', onClick: this.handleUnClick},
					'I am clicked'
				)
			}
	}
}


let buttonElement = React.createElement(Button, {name: 'A Good button'});
let currentUserElement = React.createElement(ShowCurrentUser);
let rootElement = document.getElementById('user_element');
ReactDOM.createRoot(rootElement).render(currentUserElement);

let rootElement2 = document.getElementById('button_element');
ReactDOM.createRoot(rootElement2).render(buttonElement);

