/* Experimental primary-display metadata only. No stream or geometry writes. */
static CFMutableArrayRef main_display_zoom_copy(CFArrayRef old)
{
    CFDictionaryRef stock;
    CFMutableDictionaryRef main_copy;
    CFMutableArrayRef result;
    CFIndex i, count;
    int64_t w, h, type;
    if (!old || (count=p_CFArrayGetCount(old)) < 1) return NULL;
    stock=(CFDictionaryRef)p_CFArrayGetValueAtIndex(old,0);
    if (!stock || p_CFGetTypeID(stock)!=p_CFDictionaryGetTypeID() ||
        !flight_dict_i64(stock,"widthPixels",&w) ||
        !flight_dict_i64(stock,"heightPixels",&h) || w!=800 || h!=480 ||
        (flight_dict_i64(stock,"type",&type) && type!=110)) {
        logf_u2("MAIN_ZOOM revision=main70_v1 applied=0 reason=unexpected_stock_display");
        return p_CFArrayCreateMutableCopy(NULL,0,old);
    }
    main_copy=dict_clone(stock);
    if (!main_copy) return p_CFArrayCreateMutableCopy(NULL,0,old);
    result=p_CFArrayCreateMutable(NULL,0,p_array_callbacks);
    if (!result) {
        p_CFRelease(main_copy);
        return p_CFArrayCreateMutableCopy(NULL,0,old);
    }
    /* Deliberately independent of ALTSET_DISPLAY_ZOOMFACTOR. The auxiliary
     * display must still be cloned from stock, never from this main copy. */
    set_i64(main_copy,"zoomFactor",70);
    p_CFArrayAppendValue(result,main_copy);
    for (i=1;i<count;++i)
        p_CFArrayAppendValue(result,p_CFArrayGetValueAtIndex(old,i));
    p_CFRelease(main_copy);
    logf_u2("MAIN_ZOOM revision=main70_v1 scope=display0 percent=70 geometry=800x480 geometry_unchanged=1 phone_applied=UNKNOWN");
    return result;
}
