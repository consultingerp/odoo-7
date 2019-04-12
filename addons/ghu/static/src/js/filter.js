'use strict';

var Shuffle = window.Shuffle;

var AdvisorFilter = function (element) {
  this.langs = Array.from(document.querySelectorAll('.js-languages button'));
  this.countries = Array.from(document.querySelectorAll('.js-countries button'));
  this.fields = Array.from(document.querySelectorAll('.js-fields button'));

  this.shuffle = new Shuffle(element, {
    easing: 'cubic-bezier(0.165, 0.840, 0.440, 1.000)', // easeOutQuart
  });

  this.filters = {
    langs: [],
    countries: [],
    fields: []
  };

  this._bindEventListeners();
};

/**
 * Bind event listeners for when the filters change.
 */
AdvisorFilter.prototype._bindEventListeners = function () {
  this._onLangsChange = this._handleLangsChange.bind(this);

  this.langs.forEach(function (button) {
    button.addEventListener('click', this._onLangsChange);
  }, this);

  this._onCountryChange = this._handleCountryChange.bind(this);

  this.countries.forEach(function (button) {
    button.addEventListener('click', this._onCountryChange);
  }, this);

  this._onFieldChange = this._handleFieldChange.bind(this);

  this.fields.forEach(function (button) {
    button.addEventListener('click', this._onFieldChange);
  }, this);
};

/**
 * Get the values of each checked input.
 * @return {Array.<string>}
 */
AdvisorFilter.prototype._getCurrentCountryFilters = function () {
  return this.countries.filter(function (button) {
    return button.classList.contains('active');
  }).map(function (button) {
    return button.getAttribute('data-value');
  });
};


AdvisorFilter.prototype._getCurrentLangsFilters = function () {
  return this.langs.filter(function (button) {
    return button.classList.contains('active');
  }).map(function (button) {
    return button.getAttribute('data-value');
  });
};


AdvisorFilter.prototype._getCurrentFieldFilters = function () {
    return this.fields.filter(function (button) {
      return button.classList.contains('active');
    }).map(function (button) {
      return button.getAttribute('data-value');
    });
  };


AdvisorFilter.prototype._handleLangsChange = function (evt) {
  var button = evt.currentTarget;

  // Treat these buttons like radio buttons where only 1 can be selected.
  if (button.classList.contains('active')) {
    button.classList.remove('active');
  } else {
    this.langs.forEach(function (btn) {
      btn.classList.remove('active');
    });

    button.classList.add('active');
  }

  this.filters.langs = this._getCurrentLangsFilters();
  this.filter();
};


AdvisorFilter.prototype._handleCountryChange = function (evt) {
    var button = evt.currentTarget;
  
    // Treat these buttons like radio buttons where only 1 can be selected.
    if (button.classList.contains('active')) {
      button.classList.remove('active');
    } else {
      this.countries.forEach(function (btn) {
        btn.classList.remove('active');
      });
  
      button.classList.add('active');
    }
  
    this.filters.countries = this._getCurrentCountryFilters();
    this.filter();
};

  AdvisorFilter.prototype._handleFieldChange = function (evt) {
    var button = evt.currentTarget;
  
    // Treat these buttons like radio buttons where only 1 can be selected.
    if (button.classList.contains('active')) {
      button.classList.remove('active');
    } else {
      this.fields.forEach(function (btn) {
        btn.classList.remove('active');
      });
  
      button.classList.add('active');
    }
  
    this.filters.fields = this._getCurrentFieldFilters();
    this.filter();
  };

/**
 * Filter shuffle based on the current state of filters.
 */
AdvisorFilter.prototype.filter = function () {
  if (this.hasActiveFilters()) {
    this.shuffle.filter(this.itemPassesFilters.bind(this));
  } else {
    this.shuffle.filter(Shuffle.ALL_ITEMS);
  }
};

/**
 * If any of the arrays in the `filters` property have a length of more than zero,
 * that means there is an active filter.
 * @return {boolean}
 */
AdvisorFilter.prototype.hasActiveFilters = function () {
  return Object.keys(this.filters).some(function (key) {
    return this.filters[key].length > 0;
  }, this);
};

/**
 * Determine whether an element passes the current filters.
 * @param {Element} element Element to test.
 * @return {boolean} Whether it satisfies all current filters.
 */
AdvisorFilter.prototype.itemPassesFilters = function (element) {
  var lang = this.filters.langs[0];
  var langString = element.getAttribute('data-lang');
  var langs = langString.split(",");

  var field = this.filters.fields[0];
  var fieldString = element.getAttribute('data-field');
  var fields = fieldString.split(",");

  var countryFilter = parseInt(this.filters.countries[0]);
  var country = parseInt(element.getAttribute('data-country'));

  // If there are active lang filters and this lang is not in that array.
  if (lang && !langs.includes(lang) || countryFilter &&  country !== countryFilter || field && !fields.includes(field) ) {
    return false;
  }

  return true;
};

document.addEventListener('DOMContentLoaded', function () {
  window.advisorFilter = new AdvisorFilter(document.querySelector('.advisor-container'));
});