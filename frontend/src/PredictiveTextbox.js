import React, { Component } from 'react';
import _ from 'lodash';

class PredictiveTextbox extends Component {
    constructor(props) {
        super(props);
        this.state = {
            typing: false,
            typingTimeout: 0,
            options: [],
            lastWord: '',
            prediction: 'test'
        };
    }

    render() {
        let prediction = this.state.prediction;
        let options = this.state.options;
        let lastWord = this.state.lastWord;
        return (
            <div>
                <div contentEditable="true" onInput={this.debounce}>
                    My test area.
                </div>
                <div>
                    <label style={{'color': 'gray'}}>
                        { prediction }
                    </label>
                </div>
                <label style={{'color': 'red'}}>
                    {
                        _.map(options, (option) => {
                            return lastWord + option + ', ';
                        })
                    }    
                </label>
            </div>
        );
    }

    debounce = (event) => {
        const text = event.currentTarget.textContent;
        const self = this;
        if (self.state.typingTimeout) {
            clearTimeout(self.state.typingTimeout);
        }

        self.setState({
            typing: false,
            typingTimeout: setTimeout(() => {
                this.predict(text);
            }, 500)
        });
    }

    predict = (text) => {
        let lastWord = text.split(' ').pop();
        fetch('http://localhost:5000/predict?text='+text)
            .then((res) => { 
                if (res.ok) {
                    return res.json();
                }
                else {
                    return res.error;
                }
            })
            .then(data => {
                if (typeof data === "object") {
                    this.setState({
                        prediction: text + data.prediction[0],
                        lastWord: lastWord,
                        options: data.prediction
                    });
                }
                else {
                    this.setState({
                        options: ['ERROR']
                    });
                }
            });
    }
}

export default PredictiveTextbox;
