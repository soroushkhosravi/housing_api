'use strict';
function Country(props) {
    return React.createElement('div', {
        className: "container"
    }, React.createElement('h2', {
        className: "country-name"
    }, `Country Name: ${props.name}`), React.createElement('p', {
        className: "capital"
    }, `Capital: ${props.capital}`), React.createElement('p', {
        className: "population"
    }, `Population: ${props.population}`));
}

class Button extends React.Component {
  render() {
    const name = this.props.name
    return React.createElement('button', {className: 'btn btn-primary'}, 'I am a ' + name);
  }
}


//let countryElement = React.createElement(Country, {name: 'United States', capital: 'Washington, D.C.', population: '332 million'});
let countryElement = React.createElement(Button, {name: 'Soroush'});
let rootElement = document.getElementById('like_button_container');
ReactDOM.createRoot(rootElement).render(countryElement);