var config = {
	geojsonserviceurl: '/mrconnsvc/get/',
	storeresulturl: '/mrconnsvc/store/',
	counturl: '/mrconnsvc/count/',
	enablekeyboardhooks: true,
	challenge: {
		hasWay: true,
		hasNode: true,
	},
	fixflag: {
		fixed: 100,
		notfixed: 0,
		someonebeatme: 100,
		noerrorafterall: 100,
		falsepositive: 1,
		skip: -1   
	},
	strings: {
		msgNextChallenge: 'Faites vos jeux...',
		msgMovingOnToNextChallenge: 'OK, moving right along...',
		msgZoomInForEdit: 'Please zoom in a little so we don\'t have to load a huge area from the API.'
	}
};
