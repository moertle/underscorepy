'use strict'

var $         = require('jquery')
var _         = require('underscore')
var Backbone  = require('backbone')
var bootstrap = require('bootstrap')

var SkeletonSocket = require('./socket.js')

window.Templates = {}

$(document).ready(function() {
    $('script[type="text/template"]').each(function() {
        Templates[this.id.slice(2)] = _.template(this.text)
    })
})

class App {
    constructor() {
        this._events = _.clone(Backbone.Events)
        this._events.on('connected', this.on_connected, this)
        this._events.on('add',       this.on_add,       this)
        this._events.on('update',    this.on_update,    this)
        this._events.on('delete',    this.on_delete,    this)
    }

    start(promises) {
        Promise.all(promises).then(() => {
            this.socket = new SkeletonSocket({
                onmessage: (msg) => {
                    let action = msg.action
                    delete msg.action
                    this._events.trigger(action, msg)
                }
            })
        })
    }

    on_connected() {
        console.info('Connected:', this.socket.wsurl)
    }

    on_add(msg) {
        let collection = this[msg.collection]
        if (collection) {
            collection.add(msg.data, {merge: true})
        }
    }

    on_update(msg) {
        let collection = this[msg.collection]
        if (!collection) {
            return
        }

        let key   = collection.model.prototype.idAttribute
        let value = msg.data[key]

        let model = collection.findWhere({[key]:value})
        if (model) {
            model.set(msg.data)
        }
    }

    on_delete(msg) {
        let collection = this[msg.collection]
        if (collection) {
            collection.remove(msg.id)
        }
    }
}

module.exports = App
