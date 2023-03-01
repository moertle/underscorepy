'use strict'

var $         = require('jquery')
var _         = require('underscore')
var Backbone  = require('backbone')
var bootstrap = require('bootstrap')

var App       = require('./app.js')
var Users     = require('./records/users.js')
var Sessions  = require('./records/sessions.js')

$(document).ready(function() {
    new SkeletonApp()
})

class SkeletonApp extends App {
    constructor() {
        super()

        this.users    = new Users.Collection
        this.sessions = new Sessions.Collection

        this.start([
            this.users.fetch({reset: true}),
            this.sessions.fetch({reset: true}),
            ])
    }
}
